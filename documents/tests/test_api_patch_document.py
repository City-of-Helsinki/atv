import json
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
from documents.models import Document, StatusHistory
from documents.tests.factories import DocumentFactory
from documents.tests.test_api_create_document import VALID_DOCUMENT_DATA
from services.enums import ServicePermissions
from services.tests.utils import get_user_service_client
from users.models import User
from utils.exceptions import get_error_response

VALID_OWNER_DOCUMENT_DATA = {
    "draft": False,
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
        status="handled",
        type="mysterious form",
        transaction_id="cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
        business_id="1234567-8",
        tos_function_id="f917d43aab76420bb2ec53f6684da7f7",
        tos_record_id="89837a682b5d410e861f8f3688154163",
    )
    assert document.attachments.count() == 0

    api_client = get_user_service_client(user, document.service)

    data = {
        **VALID_OWNER_DOCUMENT_DATA,
        "attachments": [
            SimpleUploadedFile(
                "document1.pdf", b"file_content", content_type="application/pdf"
            ),
        ],
    }
    with mock.patch(
        "documents.serializers.attachment.virus_scan_attachment_file", return_value=None
    ):
        response = api_client.patch(
            reverse("documents-detail", args=[document.id]), data, format="multipart"
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
    document = DocumentFactory(id="2d2b7a36-a306-4e35-990f-13aea04263ff", draft=True)
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
    assert body == get_error_response(
        "NOT_FOUND", "No Document matches the given query."
    )


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_owner_non_draft(user):
    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff", draft=False, user=user
    )
    api_client = get_user_service_client(user, document.service)

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED", "Unable to modify document - it's no longer a draft"
    )


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

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED", "Unable to modify document - it's no longer a draft"
    )


@freeze_time("2021-06-30T12:00:00")
def test_update_document_owner_invalid_fields(user):
    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff", draft=True, user=user
    )
    api_client = get_user_service_client(user, document.service)

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {
            "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
            "tos_record_id": "89837a682b5d410e861f8f3688154163",
        },  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert len(body.get("errors")) == 1
    assert body.get("errors", [])[0].get("code") == "INVALID_FIELD"
    assert "Got invalid input fields" in body.get("errors", [])[0].get("message")
    assert "tos_function_id" in body.get("errors", [])[0].get("message")
    assert "tos_record_id" in body.get("errors", [])[0].get("message")


# STAFF-RELATED ACTION


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_staff(user, service, snapshot):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.CHANGE_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.ADD_ATTACHMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        draft=True,
        service=service,
        status="handled",
    )
    assert Document.objects.count() == 1

    data = {
        **VALID_DOCUMENT_DATA,
        "attachments": [
            SimpleUploadedFile(
                "document1.pdf", b"file_content", content_type="application/pdf"
            ),
        ],
    }
    with mock.patch(
        "documents.serializers.attachment.virus_scan_attachment_file", return_value=None
    ):
        response = api_client.patch(
            reverse("documents-detail", args=[document.id]), data, format="multipart"
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
    assert body.pop("user_id", None) == str(document.user.uuid)
    snapshot.assert_match(body)


@freeze_time("2021-06-30T12:00:00+03:00")
def test_update_document_staff_non_draft(user, service, snapshot):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.CHANGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        service=service,
        draft=False,
        status="handled",
    )

    data = {**VALID_DOCUMENT_DATA}

    response = api_client.patch(reverse("documents-detail", args=[document.id]), data)

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body.pop("user_id", None) == str(document.user.uuid)
    snapshot.assert_match(body)


@freeze_time("2021-06-30T12:00:00")
def test_update_document_staff_after_lock_date(user, service):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.CHANGE_DOCUMENTS.value, group, service)
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

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED", "Unable to modify document - it's no longer a draft"
    )


@freeze_time("2021-06-30T12:00:00")
def test_update_document_staff_another_service(user, service):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.CHANGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(id="2d2b7a36-a306-4e35-990f-13aea04263ff")

    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND", "No Document matches the given query."
    )


@freeze_time("2021-06-30T12:00:00")
def test_add_user_anonymous_document(service_api_client):
    data = {
        **VALID_DOCUMENT_DATA,
    }

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )
    assert response.status_code == status.HTTP_201_CREATED
    document_id = response.json().get("id")

    user_id = "6345c12c-36c8-4e81-bd18-d66e9b1f754d"
    response = service_api_client.patch(
        reverse("documents-detail", args=[document_id]), {"user_id": user_id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert User.objects.filter(uuid=user_id).exists() is True

    body = response.json()
    assert body.get("user_id") == user_id


@freeze_time("2021-06-30T12:00:00")
def test_update_document_user(service_api_client):
    user_id = "6345c12c-36c8-4e81-bd18-d66e9b1f754d"
    new_user_id = "6345c12c-36c8-4e81-bd18-d66e9b1f754b"
    data = {**VALID_DOCUMENT_DATA, "user_id": user_id}

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )
    body = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(uuid=user_id).exists() is True
    assert body.get("user_id") == user_id

    document_id = body.get("id")
    response = service_api_client.patch(
        reverse("documents-detail", args=[document_id]), {"user_id": new_user_id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert str(Document.objects.get(id=document_id).user.uuid) == new_user_id


@freeze_time("2021-06-30T12:00:00")
def test_update_document_owner_user_id(user):
    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff",
        draft=True,
        user=user,
        status="handled",
        type="mysterious form",
        transaction_id="cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
        business_id="1234567-8",
        tos_function_id="f917d43aab76420bb2ec53f6684da7f7",
        tos_record_id="89837a682b5d410e861f8f3688154163",
    )

    assert Document.objects.count() == 1
    api_client = get_user_service_client(user, document.service)

    user_id = "6345c12c-36c8-4e81-bd18-d66e9b1f754d"
    data = {**VALID_OWNER_DOCUMENT_DATA, "user_id": user_id}
    response = api_client.patch(
        reverse("documents-detail", args=[document.id]), data, format="multipart"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not User.objects.filter(uuid=user_id).exists()

    assert response.json() == get_error_response(
        code="INVALID_FIELD", detail="Got invalid input fields: user_id."
    )


@freeze_time("2021-06-30T12:00:00")
def test_update_deletable_field(user, service):
    api_client = get_user_service_client(user, service)
    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.CHANGE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="2d2b7a36-a306-4e35-990f-13aea04263ff", service=service, deletable=True
    )
    assert Document.objects.count() == 1

    # Allow changing deletable field from True to False
    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {"deletable": False},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["deletable"] is False

    # Changing deletable to True from False isn't allowed
    response = api_client.patch(
        reverse("documents-detail", args=[document.id]),
        {"deletable": True},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@freeze_time("2021-06-30T12:00:00")
def test_create_status_history(service_api_client):
    data = {
        **VALID_DOCUMENT_DATA,
    }

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )
    assert response.status_code == status.HTTP_201_CREATED
    document_id = response.json().get("id")

    # Patch shouldn't create status history object
    response = service_api_client.patch(
        reverse("documents-detail", args=[document_id]), {"type": "new type"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert StatusHistory.objects.count() == 0

    # Creates status history object when status field changes
    response = service_api_client.patch(
        reverse("documents-detail", args=[document_id]),
        {"status": "created status history object"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert StatusHistory.objects.count() == 1


# OTHER STUFF


@freeze_time("2021-06-30T12:00:00")
def test_update_document_not_found(superuser_api_client):
    response = superuser_api_client.patch(
        reverse("documents-detail", args=[uuid4()]),
        {},  # No need to have any actual data
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND", "No Document matches the given query."
    )


@pytest.mark.parametrize("attachments", [0, 1, 2])
@pytest.mark.parametrize(
    "ip_address", ["213.255.180.34", "2345:0425:2CA1::0567:5673:23b5"]
)
def test_audit_log_is_created_when_patching(user, attachments, ip_address):
    document = DocumentFactory(draft=True, user=user)
    api_client = get_user_service_client(user, document.service)
    data = {**VALID_OWNER_DOCUMENT_DATA}

    if attachments:
        data["attachments"] = [
            SimpleUploadedFile(
                f"document{i}.pdf", b"file_content", content_type="application/pdf"
            )
            for i in range(attachments)
        ]
    with mock.patch(
        "documents.serializers.attachment.virus_scan_attachment_file", return_value=None
    ):
        api_client.patch(
            reverse("documents-detail", args=[document.id]),
            data,
            HTTP_X_FORWARDED_FOR=ip_address,
        )

    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id=str(document.pk),
            message__audit_event__target__lookup_field="pk",
            message__audit_event__target__endpoint="Document Instance",
            message__audit_event__operation="UPDATE",
            message__audit_event__actor__ip_address=ip_address,
        ).count()
        == 1
    )
