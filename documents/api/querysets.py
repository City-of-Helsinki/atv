from django.db.models import QuerySet

from services.enums import ServicePermissions
from services.models import Service
from users.models import User

from ..models import Attachment, Document


def get_document_queryset(user: User, service: Service) -> QuerySet:
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
        return Document.objects.all()

    # If the user is anonymous, don't return anything,
    # even if they're associated to a Service.
    if user.is_anonymous:
        return Document.objects.none()

    # Filter the Documents only for the user's Service
    qs_filters = {"service": service}

    # If the user doesn't have permissions to view that Service,
    # only show the Documents that belong to them
    staff_can_view = user.has_perm(ServicePermissions.VIEW_DOCUMENTS.value, service)
    staff_can_manage = user.has_perm(ServicePermissions.MANAGE_DOCUMENTS.value, service)

    if not staff_can_view and not staff_can_manage:
        qs_filters["user_id"] = user.id

    return Document.objects.filter(**qs_filters)


def get_attachment_queryset(user: User, service: Service) -> QuerySet:
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
    staff_can_manage = user.has_perm(
        ServicePermissions.MANAGE_ATTACHMENTS.value, service
    )

    if not staff_can_view and not staff_can_manage:
        qs_filters["document__user_id"] = user.id

    return Attachment.objects.filter(**qs_filters)
