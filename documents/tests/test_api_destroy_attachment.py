import random
from datetime import timezone

import pytest
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from audit_log.models import AuditLogEntry
from documents.models import Attachment
from documents.tests.factories import AttachmentFactory
from services.enums import ServicePermissions
from services.tests.utils import get_user_service_client
from utils.exceptions import get_error_response

# OWNER-RELATED ACTIONS


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_attachment_owner(user, service):
    api_client = get_user_service_client(user, service)

    attachment = AttachmentFactory(
        document__draft=True,
        document__user=user,
        document__service=service,
    )
    assert Attachment.objects.count() == 1

    response = api_client.delete(
        reverse(
            "documents-attachments-detail",
            args=[attachment.document.id, attachment.id],
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Attachment.objects.count() == 0


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_attachment_owner_someone_elses_attachment(user, service):
    api_client = get_user_service_client(user, service)

    attachment = AttachmentFactory(
        document__draft=True,
        document__service=service,
    )
    assert Attachment.objects.count() == 1

    # Check that the owner of the document is different than the one
    # making the request
    assert attachment.document.user != user

    response = api_client.delete(
        reverse(
            "documents-attachments-detail",
            args=[attachment.document.id, attachment.id],
        )
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Attachment matches the given query.",
    )


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_attachment_owner_non_draft(user, service):
    api_client = get_user_service_client(user, service)

    attachment = AttachmentFactory(
        document__draft=False,
        document__user=user,
        document__service=service,
    )
    assert Attachment.objects.count() == 1

    response = api_client.delete(
        reverse(
            "documents-attachments-detail",
            args=[attachment.document.id, attachment.id],
        )
    )

    body = response.json()

    assert Attachment.objects.count() == 1
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        "Unable to modify document - it's no longer a draft",
    )


@freeze_time("2021-06-30T12:00:00")
def test_destroy_attachment_owner_after_lock_date(user, service):
    api_client = get_user_service_client(user, service)

    attachment = AttachmentFactory(
        document__locked_after=today(timezone.utc) - relativedelta(days=1),
        document__draft=True,
        document__user=user,
        document__service=service,
    )
    assert Attachment.objects.count() == 1

    response = api_client.delete(
        reverse(
            "documents-attachments-detail",
            args=[attachment.document.id, attachment.id],
        )
    )

    body = response.json()

    assert Attachment.objects.count() == 1
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        f"Unable to modify document - it's no longer a draft. Locked at: {attachment.document.locked_after}.",
    )


# STAFF-RELATED ACTION


@freeze_time("2021-06-30T12:00:00+03:00")
@pytest.mark.parametrize("has_permission", [True, False])
def test_destroy_attachment_staff(user, service, has_permission):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_ATTACHMENTS.value, group, service)
    if has_permission:
        assign_perm(ServicePermissions.DELETE_ATTACHMENTS.value, group, service)
    user.groups.add(group)

    attachment = AttachmentFactory(
        document__service=service,
    )
    assert Attachment.objects.count() == 1

    response = api_client.delete(
        reverse(
            "documents-attachments-detail",
            args=[attachment.document.id, attachment.id],
        )
    )

    if has_permission:
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Attachment.objects.count() == 0
    else:
        body = response.json()

        assert Attachment.objects.count() == 1
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body == get_error_response(
            "PERMISSION_DENIED",
            "You do not have permission to perform this action.",
        )


# OTHER STUFF


@freeze_time("2021-06-30T12:00:00")
def test_destroy_attachment_not_found(superuser_api_client, document):
    response = superuser_api_client.delete(
        reverse(
            "documents-attachments-detail",
            args=[document.id, random.randint(0, 100)],
        )
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Attachment matches the given query.",
    )


def test_audit_log_is_created_when_destroying(user, service):
    api_client = get_user_service_client(user, service)

    attachment = AttachmentFactory(
        document__draft=True,
        document__user=user,
        document__service=service,
    )

    api_client.delete(
        reverse(
            "documents-attachments-detail",
            args=[attachment.document.id, attachment.id],
        )
    )

    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Attachment",
            message__audit_event__target__id=str(attachment.pk),
            message__audit_event__operation="DELETE",
            message__audit_event__actor__service=service.name,
        ).count()
        == 1
    )
