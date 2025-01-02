from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from helusers.utils import uuid_to_username
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
)
from rest_framework.parsers import FileUploadParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework_extensions.mixins import NestedViewSetMixin

from atv.decorators import not_allowed, service_required
from atv.exceptions import (
    DocumentLockedException,
    InvalidFieldException,
    MissingParameterException,
)
from audit_log.viewsets import AuditLoggingModelViewSet
from services.enums import ServicePermissions
from services.utils import get_service_api_key_from_request, get_service_from_request
from users.models import User
from utils.api import PageNumberPagination
from utils.uuid import is_valid_uuid

from ..consts import VALID_OWNER_PATCH_FIELDS
from ..models import Attachment, Document, StatusHistory
from ..serializers import (
    AttachmentSerializer,
    CreateAnonymousDocumentSerializer,
    CreateAttachmentSerializer,
    DocumentSerializer,
)
from ..serializers.document import (
    DocumentMetadataSerializer,
    DocumentStatisticsSerializer,
    GDPRSerializer,
)
from ..serializers.status_history import (
    CreateStatusHistorySerializer,
    StatusHistorySerializer,
)
from ..utils import get_decrypted_file
from .docs import (
    attachment_viewset_docs,
    document_gdpr_viewset,
    document_metadata_viewset_docs,
    document_statistics_viewset_docs,
    document_status_history_viewset_docs,
    document_viewset_docs,
)
from .filtersets import (
    DocumentFilterSet,
    DocumentMetadataFilterSet,
    DocumentStatisticsFilterSet,
)
from .querysets import (
    get_attachment_queryset,
    get_document_gdpr_data_queryset,
    get_document_metadata_queryset,
    get_document_queryset,
    get_document_statistics_queryset,
)


@extend_schema_view(**document_status_history_viewset_docs)
class DocumentStatusActivityViewSet(AuditLoggingModelViewSet):
    queryset = StatusHistory.objects.none()
    serializer_class = StatusHistorySerializer

    def get_queryset(self):
        request = self.request
        user = request.user
        service = get_service_from_request(request)
        api_key = get_service_api_key_from_request(request)
        qs = (
            StatusHistory.objects.filter()
            .select_related("document")
            .prefetch_related("activities")
        )
        if user.is_superuser:
            return qs

        if api_key:
            qs = qs.filter(document__service=service)
        else:
            qs = qs.filter(document__user=user)
        return qs

    def list(self, request, *args, **kwargs):
        document_id = kwargs.get("document_id")
        # Return 404 if user has no access to document or if it doesn't exist
        document = get_object_or_404(
            get_document_queryset(
                request.user,
                get_service_from_request(self.request),
                get_service_api_key_from_request(self.request),
            ),
            id=document_id,
        )
        with self.record_action(document):
            queryset = self.filter_queryset(self.get_queryset()).filter(**kwargs)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        document_id = kwargs.get("document_id")

        # Filter only for the user's documents
        document = get_object_or_404(
            get_document_queryset(
                request.user,
                get_service_from_request(self.request),
                get_service_api_key_from_request(self.request),
            ),
            id=document_id,
        )
        with self.record_action(document):
            request.data.update({"document": document.id})

            serializer = CreateStatusHistorySerializer(data=request.data)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=StatusHistorySerializer(serializer.instance[0]).data,
                status=(
                    status.HTTP_201_CREATED
                    if serializer.instance[1]
                    else status.HTTP_200_OK
                ),
            )

    @not_allowed()
    def retrieve(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def destroy(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def partial_update(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def update(self, request, *args, **kwargs):
        """Method not allowed"""


@extend_schema_view(**document_statistics_viewset_docs)
class DocumentStatisticsViewSet(AuditLoggingModelViewSet):
    queryset = Document.objects.none()
    serializer_class = DocumentStatisticsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentStatisticsFilterSet

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated
        if not get_service_api_key_from_request(self.request) and not user.has_perm(
            "users.view_document_statistics"
        ):
            raise PermissionDenied()
        service = get_service_from_request(self.request)
        return get_document_statistics_queryset(user, service)

    @not_allowed()
    def retrieve(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def destroy(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def create(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def partial_update(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def update(self, request, *args, **kwargs):
        """Method not allowed"""


@extend_schema_view(**document_gdpr_viewset)
class GDPRDataViewSet(AuditLoggingModelViewSet):
    queryset = Document.objects.none()
    serializer_class = GDPRSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    lookup_field = "user__uuid"
    http_method_names = ["get", "delete"]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated()
        if not get_service_api_key_from_request(self.request) and not user.is_superuser:
            raise PermissionDenied()
        service = get_service_from_request(self.request)
        return get_document_gdpr_data_queryset(user, service)

    def retrieve(self, request, *args, **kwargs):
        with self.record_action():
            queryset = self.filter_queryset(self.get_queryset()).filter(**kwargs)
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        with self.record_action():
            # Anonymize data
            with transaction.atomic():
                qs = self.filter_queryset(self.get_queryset()).filter(
                    deletable=True, **kwargs
                )
                Attachment.objects.filter(document__in=qs).delete()
                qs.update(user=None, content={}, business_id="")
            # Return details on documents that weren't deleted
            queryset = self.filter_queryset(self.get_queryset()).filter(**kwargs)
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)

    @not_allowed()
    def list(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def create(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def partial_update(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def update(self, request, *args, **kwargs):
        """Method not allowed"""


@extend_schema_view(**document_metadata_viewset_docs)
class DocumentMetadataViewSet(AuditLoggingModelViewSet):
    serializer_class = DocumentMetadataSerializer
    queryset = Document.objects.none()
    filter_backends = [DjangoFilterBackend]
    lookup_field = "user__uuid"
    pagination_class = PageNumberPagination
    filterset_class = DocumentMetadataFilterSet

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated()
        service_api_key = get_service_api_key_from_request(self.request)
        return get_document_metadata_queryset(user, service_api_key)

    # Use retrieve to allow using user__uuid as a lookup_field to list documents of
    # single user
    def retrieve(self, request, *args, **kwargs):
        with self.record_action():
            service_api_key = get_service_api_key_from_request(request)
            if request.user.uuid != kwargs[self.lookup_field] and not service_api_key:
                if not request.user.is_superuser:
                    raise PermissionDenied()
            if not User.objects.filter(uuid=kwargs[self.lookup_field]).exists():
                raise NotFound(detail="No user matches the given query.")
            queryset = self.filter_queryset(self.get_queryset())
            queryset = queryset.filter(**kwargs)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    @not_allowed()
    def list(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def create(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def partial_update(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def update(self, request, *args, **kwargs):
        """Method not allowed"""


@extend_schema_view(**attachment_viewset_docs)
class AttachmentViewSet(AuditLoggingModelViewSet, NestedViewSetMixin):
    serializer_class = AttachmentSerializer
    parser_classes = [MultiPartParser, FileUploadParser]
    filter_backends = [filters.OrderingFilter]
    ordering = ["-updated_at", "id"]
    queryset = Attachment.objects.none()

    def get_queryset(self):
        user = self.request.user
        service = get_service_from_request(self.request)
        service_api_key = get_service_api_key_from_request(self.request)

        return get_attachment_queryset(user, service, service_api_key)

    def retrieve(self, request, *args, **kwargs):
        attachment: Attachment = self.get_object()
        decrypted_file = get_decrypted_file(attachment.file.read(), attachment.filename)
        attachment.file.close()
        with self.record_action():
            return FileResponse(
                decrypted_file,
                as_attachment=True,
            )

    def destroy(self, request, *args, **kwargs):
        attachment = self.get_object()

        # The user is the owner of the document
        is_owner = request.user == attachment.document.user
        staff_can_delete = request.user.has_perm(
            ServicePermissions.DELETE_ATTACHMENTS, attachment.document.service
        )

        if not is_owner and not staff_can_delete:
            raise PermissionDenied()

        not_draft = is_owner and not attachment.document.draft
        is_locked = (
            attachment.document.locked_after
            and now() >= attachment.document.locked_after
        )
        if is_locked or not_draft:
            raise DocumentLockedException(
                # Only pass the locked date if it's after the date
                locked_after=attachment.document.locked_after if is_locked else None
            )
        if not (
            attachment.document.deletable or attachment.document.draft
        ) and not request.user.has_perm("users.delete_document_undeletable"):
            raise PermissionDenied(
                "File can't be deleted due to contractual obligation."
            )

        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        document_id = kwargs.get("document_id")

        if document_id is None or not is_valid_uuid(document_id):
            raise MissingParameterException(parameter="document_id")

        # Filter only for the user's documents
        document = get_object_or_404(
            get_document_queryset(
                request.user,
                get_service_from_request(self.request),
                get_service_api_key_from_request(self.request),
            ),
            id=document_id,
        )

        # The user is the owner of the document
        is_owner = request.user == document.user
        staff_can_create = request.user.has_perm(
            ServicePermissions.ADD_ATTACHMENTS, document.service
        )

        if not is_owner and not staff_can_create:
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
    def list(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def partial_update(self, request, *args, **kwargs):
        """Method not allowed"""

    @not_allowed()
    def update(self, request, *args, **kwargs):
        """Method not allowed"""


@extend_schema_view(**document_viewset_docs)
class DocumentViewSet(AuditLoggingModelViewSet):
    parser_classes = [MultiPartParser, JSONParser]
    serializer_class = DocumentSerializer
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
    queryset = Document.objects.none()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_data_extra_fields = {}

    def get_queryset(self):
        user = self.request.user
        service = get_service_from_request(self.request)
        service_api_key = get_service_api_key_from_request(self.request)
        return get_document_queryset(user, service, service_api_key)

    @action(detail=False, methods=["POST"], url_path="batch-list")
    def batch_list(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, dict):
            raise InvalidFieldException(detail="Data is not a json object.")
        document_ids = data.get("document_ids")
        if not document_ids:
            raise InvalidFieldException(detail="Field 'document_ids' is required")
        if not isinstance(document_ids, list):
            raise InvalidFieldException(
                detail="Field 'document_ids' should be a list of UUIDs"
            )
        queryset = self.get_queryset().filter(id__in=document_ids)
        with self.record_action():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @service_required()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic()
    @extend_schema(request=CreateAnonymousDocumentSerializer)
    def create(self, request, *args, **kwargs):
        service = get_service_from_request(request)
        api_key = get_service_api_key_from_request(request)

        user = request.user if not api_key else None

        if api_key and not request.user.has_perm(
            ServicePermissions.ADD_DOCUMENTS, service
        ):
            raise PermissionDenied()

        data = request.data

        user_id = data.get("user_id")
        if user_id and api_key:
            user, created = User.objects.get_or_create(
                uuid=user_id, defaults={"username": uuid_to_username(user_id)}
            )
        elif user_id and not api_key:
            raise PermissionDenied(detail="INVALID FIELD: user_id. API key required.")

        serializer = CreateAnonymousDocumentSerializer(data=data)

        # If the data is not valid, it will raise a ValidationError and return Bad
        # Request
        serializer.is_valid(raise_exception=True)

        with self.record_action():
            serializer.save(user=user, service=service)
            self.created_instance = serializer.instance
            request_data_status = request.data.get("status")
            if request_data_status:
                status_history_serializer = CreateStatusHistorySerializer(
                    data={
                        "document": self.created_instance.id,
                        "value": request_data_status,
                        "status_display_values": json.loads(
                            request.data.get("status_display_values", "{}")
                        ),
                    }
                )
                status_history_serializer.is_valid(raise_exception=True)
                status_history_serializer.save()

        return Response(
            data=DocumentSerializer(
                serializer.instance, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic()
    def partial_update(self, request, pk, *args, **kwargs):
        document = self.get_object()

        # The user is the owner of the document
        is_owner = request.user == document.user

        # The user is a staff member for the document's service
        is_staff = request.user.has_perm(
            ServicePermissions.CHANGE_DOCUMENTS, document.service
        )
        staff_can_add_attachments = request.user.has_perm(
            ServicePermissions.ADD_ATTACHMENTS, document.service
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

        attachments = request.FILES.getlist("attachments", [])

        for attached_file in attachments:
            if is_staff and not staff_can_add_attachments:
                raise PermissionDenied()
            data = {
                "document": document.id,
                "file": attached_file,
                "media_type": attached_file.content_type,
            }
            attachment_serializer = CreateAttachmentSerializer(data=data)
            attachment_serializer.is_valid(raise_exception=True)
            attachment_serializer.save()
        # Update history only if status changed.
        request_data_status = request.data.get("status")
        if request_data_status and request_data_status != document.status:
            status_history_serializer = CreateStatusHistorySerializer(
                data={
                    "document": document.id,
                    "value": request_data_status,
                    "status_display_values": json.loads(
                        request.data.get("status_display_values", "{}")
                    ),
                }
            )
            status_history_serializer.is_valid(raise_exception=True)
            status_history_serializer.save()

            # Update status_timestamp field also if the status has changed
            self.request_data_extra_fields["status_timestamp"] = timezone.now()

        return super().partial_update(request, pk, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        if self.request_data_extra_fields:
            # Request data itself is immutable so we modify the copy of the
            # data before it's given to the serializer.
            data = kwargs["data"].copy()
            data.update(self.request_data_extra_fields)
            kwargs["data"] = data
        return super().get_serializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Only allow for PATCH updates as described by the documentation
        # PUT requests will fail
        if request.method != "PATCH":
            raise MethodNotAllowed(request.method)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()

        # The user is the owner of the document
        is_owner = request.user == document.user

        # The user is a staff member for the document's service
        is_staff = request.user.has_perm(
            ServicePermissions.DELETE_DOCUMENTS, document.service
        )

        if not is_owner and not is_staff:
            raise PermissionDenied()

        not_draft = is_owner and not document.draft
        is_locked = document.locked_after and now() >= document.locked_after
        if is_locked or not_draft:
            raise DocumentLockedException(
                # Only pass the locked date if it's after the date
                locked_after=document.locked_after if is_locked else None
            )

        if not (document.deletable or document.draft) and not request.user.has_perm(
            "users.delete_document_undeletable"
        ):
            raise PermissionDenied(
                detail="Document can't be deleted due to contractual obligation."
            )

        return super().destroy(request, *args, **kwargs)
