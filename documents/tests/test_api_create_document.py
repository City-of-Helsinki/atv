import datetime
import json
import uuid
from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from audit_log.models import AuditLogEntry
from documents.models import Attachment, Document
from services.tests.utils import get_user_service_client
from users.models import User
from utils.exceptions import get_error_response

VALID_DOCUMENT_DATA = {
    "status": "handled",
    "status_display_values": json.dumps({"fi": "Käsitelty"}),
    "type": "mysterious form",
    "human_readable_type": json.dumps({"en": "Mysterious Form"}),
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "business_id": "1234567-8",
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "metadata": json.dumps({"created_by": "alex", "testing": True}),
    "deletable": False,
    "document_language": "en",
    "content_schema_url": "https://schema.fi",
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


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_anonymous_document(service_api_client, snapshot):
    data = {
        **VALID_DOCUMENT_DATA,
        "attachments": [
            SimpleUploadedFile(
                "document1.pdf", b"file_content", content_type="application/pdf"
            ),
            SimpleUploadedFile(
                "document2.pdf", b"file_content", content_type="application/pdf"
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
    assert Document.objects.count() == 1
    assert Attachment.objects.count() == 2

    document = Document.objects.first()
    assert document.attachments.count() == 2
    assert document.user is None
    attachment1 = document.attachments.first()
    attachment2 = document.attachments.last()

    body = response.json()
    assert uuid.UUID(body.pop("id")) == document.id
    assert body.pop("attachments", []) == [
        {
            "created_at": "2021-06-30T12:00:00+03:00",
            "filename": "document1.pdf",
            "href": f"http://testserver/v1/documents/{document.id}/attachments/{attachment1.id}/",
            "id": attachment1.id,
            "media_type": "application/pdf",
            "size": 12,
            "updated_at": "2021-06-30T12:00:00+03:00",
        },
        {
            "created_at": "2021-06-30T12:00:00+03:00",
            "filename": "document2.pdf",
            "href": f"http://testserver/v1/documents/{document.id}/attachments/{attachment2.id}/",
            "id": attachment2.id,
            "media_type": "application/pdf",
            "size": 12,
            "updated_at": "2021-06-30T12:00:00+03:00",
        },
    ]
    snapshot.assert_match(body)


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_authenticated_document(user, service, snapshot):
    """Normal user creates a document which is attached to his/her account."""
    api_client = get_user_service_client(user, service)

    delete_after_date = "2022-12-12"
    response = api_client.post(
        reverse("documents-list"),
        {**VALID_DOCUMENT_DATA, "delete_after": delete_after_date},
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Document.objects.count() == 1

    document = Document.objects.first()
    assert document.user == user
    assert document.service == service
    assert document.delete_after == datetime.date(day=12, month=12, year=2022)

    body = response.json()
    assert uuid.UUID(body.pop("id")) == document.id
    assert body.pop("user_id") == str(user.uuid)
    snapshot.assert_match(body)

    response = api_client.get(reverse("documents-detail", args=[document.id]))
    assert response.status_code == status.HTTP_200_OK


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_anonymous_document_no_service(api_client):
    response = api_client.post(
        reverse("documents-list"), VALID_DOCUMENT_DATA, format="multipart"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "content", ["this shouldn't be allowed", '{"id": 1 "name": "Test"}']
)
def test_create_document_invalid_json_content(service_api_client, content):
    data = {**VALID_DOCUMENT_DATA, "content": content}

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Document.objects.count() == 0
    assert Attachment.objects.count() == 0

    body = response.json()
    assert body == get_error_response(
        "INVALID_FIELD", "content: Value must be valid JSON."
    )


def test_create_document_invalid_fields(service_api_client):
    data = {**VALID_DOCUMENT_DATA, "invalid_field": True}

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Document.objects.count() == 0
    assert Attachment.objects.count() == 0

    body = response.json()
    assert body == get_error_response(
        "INVALID_FIELD", "Got invalid input fields: invalid_field"
    )


@override_settings(MAX_FILE_UPLOAD_ALLOWED=10)
def test_create_document_many_files(service_api_client):
    data = {
        **VALID_DOCUMENT_DATA,
        "attachments": [
            SimpleUploadedFile(
                f"document{i}.pdf", b"file_content", content_type="application/pdf"
            )
            for i in range(1, 15)
        ],
    }

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Document.objects.count() == 0
    assert Attachment.objects.count() == 0

    body = response.json()
    assert body == get_error_response(
        "MAXIMUM_FILE_COUNT_EXCEEDED", "File upload is limited to 10"
    )


@override_settings(MAX_FILE_SIZE=50)
def test_create_document_file_limit(service_api_client, settings):
    data = {
        **VALID_DOCUMENT_DATA,
        "attachments": [
            SimpleUploadedFile(
                "document1.pdf",
                b"x" * 10000,
                content_type="application/pdf",
            )
        ],
    }

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Document.objects.count() == 0
    assert Attachment.objects.count() == 0

    body = response.json()
    assert body == get_error_response(
        "MAXIMUM_FILE_SIZE_EXCEEDED",
        "Cannot upload files larger than 0.0 Mb: 0.01 Mb",
    )


def test_create_document_no_attachments(service_api_client):
    assert Document.objects.count() == 0
    assert Attachment.objects.count() == 0

    response = service_api_client.post(
        reverse("documents-list"), VALID_DOCUMENT_DATA, format="multipart"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Document.objects.count() == 1
    assert Attachment.objects.count() == 0

    body = response.json()
    assert body.get("attachments") == []


@pytest.mark.parametrize("attachments", [0, 1, 2])
@pytest.mark.parametrize(
    "ip_address", [" 213.255.180.34 ", "2345:0425:2CA1::0567:5673:23b5"]
)
def test_audit_log_is_created_when_creating(
    service_api_client, attachments, ip_address
):
    data = {**VALID_DOCUMENT_DATA}
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
        response = service_api_client.post(
            reverse("documents-list"),
            data,
            format="multipart",
            HTTP_X_FORWARDED_FOR=ip_address,
        ).json()

    assert Document.objects.count() == 1

    assert Attachment.objects.count() == attachments
    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id=response["id"],
            message__audit_event__operation="CREATE",
            message__audit_event__actor__ip_address=ip_address.strip(),  # remove whitespaces to verify correct parsing
        ).count()
        == 1
    )


def test_create_document_user_id(service_api_client):
    user_id = "6345c12c-36c8-4e81-bd18-d66e9b1f754d"
    data = {**VALID_DOCUMENT_DATA, "user_id": user_id}

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )
    body = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert Document.objects.count() == 1
    assert User.objects.filter(uuid=user_id).exists() is True
    assert body.get("user_id") == user_id


def test_create_document_owner_user_id(user, service):
    data = {**VALID_DOCUMENT_DATA, "user_id": "6345c12c-36c8-4e81-bd18-d66e9b1f754d"}
    api_client = get_user_service_client(user, service)

    response = api_client.post(reverse("documents-list"), data, format="multipart")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    body = response.json()

    assert body == get_error_response(
        code="PERMISSION_DENIED", detail="INVALID FIELD: user_id. API key required."
    )
