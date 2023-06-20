from django.db.models import Count, Prefetch, QuerySet
from rest_framework.exceptions import PermissionDenied

from services.enums import ServicePermissions
from services.models import Service, ServiceAPIKey
from users.models import User

from ..models import Activity, Attachment, Document, StatusHistory


def get_document_statistics_queryset(user: User, service: Service) -> QuerySet:
    qs = (
        Document.objects.only(
            "id",
            "created_at",
            "service",
            "status",
            "type",
            "transaction_id",
            "human_readable_type",
            "user__uuid",
            "deletable",
        )
        .select_related("service", "user")
        .prefetch_related(
            Prefetch(
                "attachments",
                queryset=Attachment.objects.only("document_id", "filename"),
            )
        )
    ).order_by("-created_at")
    if user.has_perm("users.view_document_statistics") or user.is_superuser:
        return qs

    return qs.filter(service=service)


def get_document_gdpr_data_queryset(user: User, service: Service) -> QuerySet:
    qs = (
        Document.objects.only(
            "id",
            "created_at",
            "service",
            "type",
            "human_readable_type",
            "user__uuid",
            "deletable",
        )
        .select_related("service", "user")
        .prefetch_related(
            Prefetch(
                "attachments",
                queryset=Attachment.objects.only("document_id", "filename"),
            )
        )
    )

    if not user.is_superuser:
        qs = qs.filter(service=service)
    return qs


def get_document_metadata_queryset(
    user: User, api_key: ServiceAPIKey = None
) -> QuerySet:
    """
    Superusers and staff(API key) are allowed to see document metadata of all services for all users.
    Token users can only see their own documents metadata from across all services.
    """
    queryset = (
        Document.objects.only(
            "created_at",
            "updated_at",
            "status",
            "status_display_values",
            "status_timestamp",
            "id",
            "service",
            "type",
            "human_readable_type",
            "user__id",
            "transaction_id",
            "document_language",
            "content_schema_url",
        )
        .select_related("service", "user")
        .prefetch_related(
            Prefetch(
                "status_histories",
                queryset=StatusHistory.objects.prefetch_related(
                    Prefetch(
                        "activities",
                        queryset=Activity.objects.filter(show_to_user=True),
                    )
                ),
            )
        )
        .order_by("-status_timestamp")
    )

    if user.is_superuser or api_key:
        return queryset
    else:
        return queryset.filter(user=user)


def get_document_queryset(
    user: User, service: Service, api_key: ServiceAPIKey = None
) -> QuerySet:
    """
    Only allow for the user to see Documents that belong to them or their Service.

    If the user is:
        - superuser, they can see everything
        - staff, they can see only Documents for their Service
        - authenticated, they can see only their own Documents
        - anonymous (no valid authentication), they can't see anything
    """

    # If the user is a superuser, return the whole set
    if user.is_superuser:
        return (
            Document.objects.all()
            .select_related("user", "service")
            .prefetch_related("attachments", "status_histories__activities")
        )

    # If the user is anonymous, don't return anything,
    # even if they're associated to a Service.
    if user.is_anonymous:
        return Document.objects.none()

    # Filter the Documents only for the user's Service
    qs_filters = {"service": service}

    # If the user doesn't have permissions to view that Service,
    # only show the Documents that belong to them
    staff_can_view = user.has_perm(ServicePermissions.VIEW_DOCUMENTS.value, service)

    if not staff_can_view:
        if api_key:
            raise PermissionDenied()

        qs_filters["user_id"] = user.id

    return (
        Document.objects.filter(**qs_filters)
        .select_related("user", "service")
        .prefetch_related("attachments", "status_histories")
    )


def get_attachment_queryset(
    user: User, service: Service, api_key: ServiceAPIKey = None
) -> QuerySet:
    """
    Only allow for the user to see Attachments that belong to their Documents
    or their Service.

    If the user is:
        - superuser, they can see everything
        - staff, they can see only Attachments for Documents of their Service
        - authenticated, they can see only their own Attachments
        - anonymous (no valid authentication), they can't see anything
    """
    # If the user is a superuser, return the whole set
    if user.is_superuser:
        return Attachment.objects.all()

    # If the user is anonymous, don't return anything,
    # even if they're associated to a Service.
    if user.is_anonymous:
        return Attachment.objects.none()

    # Filter the Documents only for the user's Service
    qs_filters = {"document__service": service}

    # If the user doesn't have permissions to view that Service,
    # only show the Documents that belong to them
    staff_can_view = user.has_perm(ServicePermissions.VIEW_ATTACHMENTS.value, service)

    if not staff_can_view:
        if api_key:
            raise PermissionDenied()

        qs_filters["document__user_id"] = user.id

    return Attachment.objects.filter(**qs_filters)
