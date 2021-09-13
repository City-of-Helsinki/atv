from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status
from rest_framework.exceptions import MethodNotAllowed, NotFound, PermissionDenied
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from atv.decorators import login_required, service_api_key_required, staff_required
from atv.exceptions import ValidationError
from audit_log.viewsets import AuditLoggingModelViewSet
from services.enums import ServicePermissions

from ..models import Attachment, Document
from ..serializers import (
    AttachmentSerializer,
    CreateAnonymousDocumentSerializer,
    CreateAttachmentSerializer,
    DocumentSerializer,
)
from .docs import attachment_viewset_docs, document_viewset_docs
from .filtersets import DocumentFilterSet


@extend_schema_view(**attachment_viewset_docs)
class AttachmentViewSet(AuditLoggingModelViewSet, NestedViewSetMixin):
    permission_classes = [IsAdminUser]
    serializer_class = AttachmentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ["-updated_at", "id"]

    def get_queryset(self):
        """
        Only allow for the user to see Attachments that belong to their Documents
        or their Service.

        If the user is:
            - superuser, they can see everything
            - staff, they can see only Attachments for Documents of their Service
            - authenticated, they can see only their own Attachments
            - anonymous (no valid authentication), they can't see anything
        """
        user = self.request.user

        # If the user is a superuser, return the whole set
        if user.is_superuser:
            return Attachment.objects.all()

        # If the user is anonymous, don't return anything,
        # even if they're associated to a Service.
        if user.is_anonymous:
            return Attachment.objects.none()

        qs_filters = {}

        # Filter the Documents only for the user's Service
        if service := self.request.service:
            qs_filters["document__service"] = service

        # If the user doesn't have permissions to view that Service,
        # only show the Documents that belong to them
        if not user.has_perm(
            ServicePermissions.VIEW_ATTACHMENTS.value, qs_filters.get("service")
        ):
            qs_filters = {"document__user_id": user.id}

        return Attachment.objects.filter(**qs_filters)

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)


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
        """
        Only allow for the user to see Documents that belong to them or their Service.

        If the user is:
            - superuser, they can see everything
            - staff, they can see only Documents for their Service
            - authenticated, they can see only their own Documents
            - anonymous (no valid authentication), they can't see anything
        """
        user = self.request.user

        # If the user is a superuser, return the whole set
        if user.is_superuser:
            return Document.objects.all()

        # If the user is anonymous, don't return anything,
        # even if they're associated to a Service.
        if user.is_anonymous:
            return Document.objects.none()

        qs_filters = {}

        # Filter the Documents only for the user's Service
        if service := self.request.service:
            qs_filters["service"] = service

        # If the user doesn't have permissions to view that Service,
        # only show the Documents that belong to them
        if not user.has_perm(
            ServicePermissions.VIEW_DOCUMENTS.value, qs_filters.get("service")
        ):
            qs_filters = {"user_id": user.id}

        return Document.objects.filter(**qs_filters)

    @staff_required(required_permission=ServicePermissions.VIEW_DOCUMENTS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic()
    @service_api_key_required()
    @extend_schema(request=CreateAnonymousDocumentSerializer)
    def create(self, request, *args, **kwargs):
        data = request.data

        serializer = CreateAnonymousDocumentSerializer(data=data)

        # If the data is not valid, it will raise a ValidationError and return Bad Request
        serializer.is_valid(raise_exception=True)

        with self.record_action():
            serializer.save(service=request.service)
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
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist as e:
            raise NotFound(e)

        # The user is the owner of the document
        is_owner = request.user == document.user

        # The user is a staff member for the document's service
        is_staff = request.user.has_perm(
            ServicePermissions.MANAGE_DOCUMENTS, document.service
        )

        if not is_owner and not is_staff:
            raise PermissionDenied(
                _("You do not have permission to perform this action.")
            )

        if is_owner and not document.draft:
            raise ValidationError(
                _("You cannot modify a document which is not a draft")
            )

        if is_staff and ("content" in request.data or "attachments" in request.data):
            raise ValidationError(_("You cannot modify the contents of the document"))

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
