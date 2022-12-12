from datetime import timezone
from unittest import mock
from uuid import uuid4

import pytest
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from audit_log.models import AuditLogEntry
from documents.models import Attachment, Document, StatusHistory
from documents.tests.factories import DocumentFactory
from documents.tests.test_api_create_document import VALID_DOCUMENT_DATA
from services.enums import ServicePermissions
from services.tests.factories import ServiceFactory
from services.tests.utils import get_user_service_client
from utils.exceptions import get_error_response

# OWNER-RELATED ACTIONS


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_owner(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        draft=True,
        user=user,
        service=service,
    )
    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_owner_someone_elses_document(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        draft=True,
        service=service,
    )
    assert Document.objects.count() == 1

    # Check that the owner of the document is different than the one
    # making the request
    assert document.user != user

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Document matches the given query.",
    )


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_owner_non_draft(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        draft=False,
        user=user,
        service=service,
    )

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        "Unable to modify document - it's no longer a draft",
    )


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_owner_after_lock_date(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        locked_after=today(timezone.utc) - relativedelta(days=1),
        draft=True,
        user=user,
        service=service,
    )

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        f"Unable to modify document - it's no longer a draft. Locked at: {document.locked_after}.",
    )


# STAFF-RELATED ACTION


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_staff(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        draft=True,
        service=service,
    )
    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_staff_non_draft(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        service=service,
        draft=False,
    )

    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_staff_after_lock_date(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        draft=True,
        locked_after=today(timezone.utc) - relativedelta(days=1),
        service=service,
    )

    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        f"Unable to modify document - it's no longer a draft. Locked at: {document.locked_after}.",
    )


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_staff_another_service(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory()

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Document matches the given query.",
    )


# OTHER STUFF


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_not_found(superuser_api_client):
    response = superuser_api_client.delete(reverse("documents-detail", args=[uuid4()]))

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Document matches the given query.",
    )


def test_gdpr_delete_user_data_service_user(user, service_api_client):
    data = {
        **VALID_DOCUMENT_DATA,
        "user_id": user.uuid,
        "deletable": True,
        "attachments": [
            SimpleUploadedFile(
                "document1.pdf", b"file_content", content_type="application/pdf"
            ),
        ],
    }
    with mock.patch(
        "documents.serializers.attachment.virus_scan_attachment_file", return_value=None
    ):
        response = service_api_client.post(
            reverse("documents-list"), data, format="multipart"
        )
        assert response.status_code == status.HTTP_201_CREATED

        data["deletable"] = False
        data["attachments"] = [
            SimpleUploadedFile(
                "document2.pdf", b"file_content", content_type="application/pdf"
            ),
        ]
        response = service_api_client.post(
            reverse("documents-list"), data, format="multipart"
        )
        assert response.status_code == status.HTTP_201_CREATED

    other_service = ServiceFactory()
    DocumentFactory(user=user, service=other_service, deletable=False)

    assert Document.objects.count() == 3
    assert Attachment.objects.count() == 2

    response = service_api_client.get(reverse("gdpr-api-detail", args=[user.uuid]))
    assert response.status_code == status.HTTP_200_OK
    body = response.data
    assert body["data"]["total_deletable"] == 1
    assert body["data"]["total_undeletable"] == 1

    response = service_api_client.delete(reverse("gdpr-api-detail", args=[user.uuid]))
    assert response.status_code == status.HTTP_200_OK

    body = response.data
    assert body["data"]["total_deletable"] == 0
    assert body["data"]["total_undeletable"] == 1

    # Documents are anonymized
    assert Document.objects.count() == 3
    for document in Document.objects.filter(deletable=True).values(
        "content", "business_id", "user_id"
    ):
        assert document["content"] == {}
        assert document["business_id"] == ""
        assert document["user_id"] is None

    assert Attachment.objects.count() == 1


def test_gdpr_delete_user(user, service):
    api_client = get_user_service_client(user, service)

    response = api_client.delete(reverse("gdpr-api-detail", args=[user.uuid]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_gdpr_delete_anonymous(api_client, user):
    response = api_client.delete(reverse("gdpr-api-detail", args=[user.uuid]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@freeze_time("2021-06-30T12:00:00+03:00")
def test_statushistory_is_destroyed_with_document(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.CHANGE_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(draft=True, service=service, status="status")
    assert Document.objects.count() == 1

    # Patch to create status history
    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {"status": "new_status", "type": "updated"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert StatusHistory.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0
    assert StatusHistory.objects.count() == 0


@pytest.mark.parametrize(
    "ip_address", ["213.255.180.34", "2345:0425:2CA1::0567:5673:23b5"]
)
def test_audit_log_is_created_when_destroying(user, service, ip_address):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(draft=True, user=user, service=service)

    api_client.delete(
        reverse("documents-detail", args=[document.id]), HTTP_X_FORWARDED_FOR=ip_address
    )

    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id=str(document.pk),
            message__audit_event__operation="DELETE",
            message__audit_event__target__lookup_field="pk",
            message__audit_event__target__endpoint="Document Instance",
            message__audit_event__actor__service=service.name,
            message__audit_event__actor__ip_address=ip_address,
        ).count()
        == 1
    )
