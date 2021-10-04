from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from atv.decorators import login_required, not_allowed, service_required
from atv.exceptions import (
    DocumentLockedException,
    InvalidFieldException,
    MissingParameterException,
)
from audit_log.viewsets import AuditLoggingModelViewSet
from services.enums import ServicePermissions
from services.utils import get_service_from_request

from ..consts import VALID_OWNER_PATCH_FIELDS
from ..models import Attachment
from ..serializers import (
    AttachmentSerializer,
    CreateAnonymousDocumentSerializer,
    CreateAttachmentSerializer,
    DocumentSerializer,
)
from .docs import attachment_viewset_docs, document_viewset_docs
from .filtersets import DocumentFilterSet
from .querysets import get_attachment_queryset, get_document_queryset


@extend_schema_view(**attachment_viewset_docs)
class AttachmentViewSet(AuditLoggingModelViewSet, NestedViewSetMixin):
    permission_classes = [AllowAny]
    serializer_class = AttachmentSerializer
    parser_classes = [MultiPartParser, FileUploadParser]
    filter_backends = [filters.OrderingFilter]
    ordering = ["-updated_at", "id"]

    def get_queryset(self):
        user = self.request.user
        service = get_service_from_request(self.request)

        return get_attachment_queryset(user, service)

    @login_required()
    def retrieve(self, request, pk, *args, **kwargs):
        attachment: Attachment = self.get_object()

        return FileResponse(
            attachment.file,
            as_attachment=True,
        )

    @login_required()
    def destroy(self, request, *args, **kwargs):
        attachment = self.get_object()

        # The user is the owner of the document
        is_owner = request.user == attachment.document.user

        # Only owners are allowed to remove the attachments,
        # staff users aren't.
        if not is_owner:
            raise PermissionDenied()

        not_draft = is_owner and not attachment.document.draft
        is_locked = (
            attachment.document.locked_after
            and now() >= attachment.document.locked_after
        )
        if is_locked or not_draft:
            raise DocumentLockedException(
                # Only pass the locked date if it's after the date
                locked_after=attachment.document.locked_after
                if is_locked
                else None
            )

        return super().destroy(request, *args, **kwargs)

    @login_required()
    def create(self, request, *args, **kwargs):
        document_id = kwargs.get("document_id")
        if not document_id:
            raise MissingParameterException(parameter="document_id")

        # Filter only for the user's documents
        document = get_object_or_404(
            get_document_queryset(
                request.user,
                get_service_from_request(self.request),
            ),
            id=document_id,
        )

        # The user is the owner of the document
        is_owner = request.user == document.user

        if not is_owner:
            raise PermissionDenied()

        if is_owner and not document.draft:
            raise DocumentLockedException()

        file = request.data.get("file")

        data = {
            "document": document.id,
            "file": file,
            "media_type": file.content_type,
        }
        attachment_serializer = CreateAttachmentSerializer(data=data)
        attachment_serializer.is_valid(raise_exception=True)

        with self.record_action():
            attachment_serializer.save()
            self.created_instance = attachment_serializer.instance

        return Response(
            AttachmentSerializer(
                attachment_serializer.instance, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @not_allowed()
    def partial_update(self, request, *args, **kwargs):
        pass

    @not_allowed()
    def update(self, request, *args, **kwargs):
        pass


@extend_schema_view(**document_viewset_docs)
class DocumentViewSet(AuditLoggingModelViewSet):
    parser_classes = [MultiPartParser]
    serializer_class = DocumentSerializer
    # Permission checking is done by the decorators on a method basis
    permission_classes = [AllowAny]
    # Filtering/sorting
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]
    search_fields = ["metadata"]
    filterset_class = DocumentFilterSet

    def get_queryset(self):
        user = self.request.user
        service = get_service_from_request(self.request)

        return get_document_queryset(user, service)

    @login_required()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @login_required()
    @service_required()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic()
    @extend_schema(request=CreateAnonymousDocumentSerializer)
    def create(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        service = get_service_from_request(request)

        data = request.data

        serializer = CreateAnonymousDocumentSerializer(data=data)

        # If the data is not valid, it will raise a ValidationError and return Bad Request
        serializer.is_valid(raise_exception=True)

        with self.record_action():
            serializer.save(user=user, service=service)
            self.created_instance = serializer.instance

        return Response(
            data=DocumentSerializer(
                serializer.instance, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic()
    @login_required()
    def partial_update(self, request, pk, *args, **kwargs):
        document = self.get_object()

        # The user is the owner of the document
        is_owner = request.user == document.user

        # The user is a staff member for the document's service
        is_staff = request.user.has_perm(
            ServicePermissions.MANAGE_DOCUMENTS, document.service
        )

        if not is_owner and not is_staff:
            raise PermissionDenied()

        if is_owner:
            if not document.draft:
                raise DocumentLockedException()

            # Check that the fields on the input are only the ones allowed for owners
            keys = set(request.data.keys())
            if not keys.issubset(VALID_OWNER_PATCH_FIELDS):
                raise InvalidFieldException(fields=keys - VALID_OWNER_PATCH_FIELDS)

        if is_staff and ("content" in request.data or "attachments" in request.data):
            raise PermissionDenied(_("You cannot modify the contents of the document"))

        attachments = request.FILES.getlist("attachments", [])

        for attached_file in attachments:
            data = {
                "document": document.id,
                "file": attached_file,
                "media_type": attached_file.content_type,
            }
            attachment_serializer = CreateAttachmentSerializer(data=data)
            attachment_serializer.is_valid(raise_exception=True)
            attachment_serializer.save()

        return super().partial_update(request, pk, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Only allow for PATCH updates as described by the documentation
        # PUT requests will fail
        if request.method != "PATCH":
            raise MethodNotAllowed(request.method)

        return super().update(request, *args, **kwargs)

    @login_required()
    def destroy(self, request, *args, **kwargs):
        document = self.get_object()

        # The user is the owner of the document
        is_owner = request.user == document.user

        # The user is a staff member for the document's service
        is_staff = request.user.has_perm(
            ServicePermissions.MANAGE_DOCUMENTS, document.service
        )

        if not is_owner and not is_staff:
            raise PermissionDenied()

        not_draft = is_owner and not document.draft
        is_locked = document.locked_after and now() >= document.locked_after
        if is_locked or not_draft:
            raise DocumentLockedException(
                # Only pass the locked date if it's after the date
                locked_after=document.locked_after
                if is_locked
                else None
            )

        return super().destroy(request, *args, **kwargs)
