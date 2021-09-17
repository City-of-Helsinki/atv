import json
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
from documents.models import Document
from documents.tests.factories import DocumentFactory
from services.enums import ServicePermissions
from services.tests.utils import get_user_service_client
from utils.tests import assert_in_errors

VALID_DOCUMENT_DATA = {
    "status": "handled",
    "type": "mysterious form",
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "business_id": "1234567-8",
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "metadata": json.dumps({"created_by": "alex", "testing": True}),
    "content": json.dumps(
        {
            "formData": {
                "firstName": "Dolph",
                "lastName": "Lundgren",
                "birthDate": "3.11.1957",
            },
            "reasonForApplication": "No reason, just testing",
        }
    ),
}


# OWNER-RELATED ACTIONS


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_owner(user, snapshot):
    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        draft=True,
        user=user,
    )
    assert document.attachments.count() == 0

    api_client = get_user_service_client(user, document.service)

    data = {
        **VALID_DOCUMENT_DATA,
        "attachments": [
            SimpleUploadedFile(
                "document1.pdf", b"file_content", content_type="application/pdf"
            ),
        ],
    }

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        data,
        format="multipart",
    )

    assert Document.objects.count() == 1
    assert document.attachments.count() == 1

    body = response.json()
    attachment = document.attachments.first()

    assert body.pop("attachments", []) == [
        {
            "created_at": "2021-06-30T12:00:00+03:00",
            "filename": "document1.pdf",
            "href": f"http://testserver/v1/documents/2d2b7a36-a306-4e35-990f-13aea04263ff/attachments/{attachment.id}/",
            "id": attachment.id,
            "media_type": "application/pdf",
            "size": 12,
            "updated_at": "2021-06-30T12:00:00+03:00",
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert body.pop("user_id", None) == str(document.user.uuid) == str(user.uuid)

    snapshot.assert_match(body)


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_owner_someone_elses_document(
    user,
):
    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        draft=True,
    )
    api_client = get_user_service_client(user, document.service)
    # Check that the owner of the document is different than the one
    # making the request
    assert document.user != user

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body.get("detail", "") == "Not found."


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_owner_non_draft(user):
    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        draft=False,
        user=user,
    )
    api_client = get_user_service_client(user, document.service)

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert_in_errors("You cannot modify a document which is not a draft", body)


@freeze_time("2021-06-30T12:00:00")
def test_update_document_owner_after_lock_date(user):
    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        locked_after=today() - relativedelta(days=1),
        draft=True,
        user=user,
    )
    api_client = get_user_service_client(user, document.service)

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert_in_errors("Cannot update a Document after it has been locked", body)


# STAFF-RELATED ACTION


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_staff(user, service, snapshot):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.MANAGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        draft=True,
        service=service,
    )
    assert Document.objects.count() == 1

    data = {**VALID_DOCUMENT_DATA}
    data.pop("content")

    response = api_client.patch(reverse("documents-detail", args=[document.id]), data)

    assert Document.objects.count() == 1

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body.pop("user_id", None) == str(document.user.uuid)
    snapshot.assert_match(body)


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_staff_non_draft(user, service, snapshot):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.MANAGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        service=service,
        draft=False,
    )

    data = {**VALID_DOCUMENT_DATA}
    data.pop("content")

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        data,
    )

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body.pop("user_id", None) == str(document.user.uuid)
    snapshot.assert_match(body)


@freeze_time("2021-06-30T12:00:00")
def test_update_document_staff_after_lock_date(user, service):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.MANAGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        locked_after=today() - relativedelta(days=1),
        service=service,
    )

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert_in_errors("Cannot update a Document after it has been locked", body)


@freeze_time("2021-06-30T12:00:00")
def test_update_document_staff_another_service(user, service):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.MANAGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
    )

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body.get("detail", "") == "Not found."


@freeze_time("2021-06-30T12:00:00")
def test_update_document_staff_update_content_fails(user, service):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.MANAGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        service=service,
    )

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {"content": json.dumps({"value": "secret stuff"})},
    )

    body = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert_in_errors("You cannot modify the contents of the document", body)


@freeze_time("2021-06-30T12:00:00")
def test_update_document_staff_update_attachments_fails(user, service):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.MANAGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        service=service,
    )

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {
            "attachments": [
                SimpleUploadedFile(
                    "document1.pdf", b"file_content", content_type="application/pdf"
                )
            ]
        },
    )

    body = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert_in_errors("You cannot modify the contents of the document", body)


# OTHER STUFF


@freeze_time("2021-06-30T12:00:00")
def test_update_document_not_found(superuser_api_client):
    response = superuser_api_client.patch(
        reverse("documents-detail", args=[uuid4()]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert body.get("detail", "") == "Not found."


@pytest.mark.parametrize("attachments", [0, 1, 2])
def test_audit_log_is_created_when_patching(user, attachments):
    document = DocumentFactory(draft=True, user=user)
    api_client = get_user_service_client(user, document.service)
    data = {**VALID_DOCUMENT_DATA}
    data.pop("content")

    if attachments:
        data["attachments"] = [
            SimpleUploadedFile(
                f"document{i}.pdf", b"file_content", content_type="application/pdf"
            )
            for i in range(attachments)
        ]

    api_client.patch(reverse("documents-detail", args=[document.id]), data)

    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id=str(document.pk),
            message__audit_event__operation="UPDATE",
        ).count()
        == 1
    )
