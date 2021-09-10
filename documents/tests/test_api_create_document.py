import json
import uuid

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from audit_log.models import AuditLogEntry
from documents.models import Attachment, Document

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


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_document(service_api_client, snapshot):
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

    # Patch the document auto-generated UUID to always have the same value
    # to have deterministic tests
    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Document.objects.count() == 1
    assert Attachment.objects.count() == 2

    document = Document.objects.first()
    assert document.attachments.count() == 2
    attachment1 = document.attachments.first()
    attachment2 = document.attachments.last()

    body = response.json()
    assert uuid.UUID(body.pop("id")) == document.id
    assert body.pop("attachments", []) == [
        {
            "created_at": "2021-06-30T12:00:00+03:00",
            "filename": "document2.pdf",
            "href": f"http://testserver/v1/documents/{document.id}/attachments/{attachment2.id}/",
            "id": attachment2.id,
            "media_type": "application/pdf",
            "size": 12,
            "updated_at": "2021-06-30T12:00:00+03:00",
        },
        {
            "created_at": "2021-06-30T12:00:00+03:00",
            "filename": "document1.pdf",
            "href": f"http://testserver/v1/documents/{document.id}/attachments/{attachment1.id}/",
            "id": attachment1.id,
            "media_type": "application/pdf",
            "size": 12,
            "updated_at": "2021-06-30T12:00:00+03:00",
        },
    ]
    snapshot.assert_match(body)


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
    assert body == {"content": ["Value must be valid JSON."]}


def test_create_document_invalid_fields(service_api_client):
    data = {**VALID_DOCUMENT_DATA, "invalid_field": True}

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Document.objects.count() == 0
    assert Attachment.objects.count() == 0

    body = response.json()
    assert body == {"errors": ["Got invalid input fields: invalid_field"]}


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
    assert body == {
        "errors": [f"File upload is limited to {settings.MAX_FILE_UPLOAD_ALLOWED}"]
    }


def test_create_document_file_limit(service_api_client):
    data = {
        **VALID_DOCUMENT_DATA,
        "attachments": [
            SimpleUploadedFile(
                "document1.pdf",
                b"x" * (settings.MAX_FILE_SIZE + 1),
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
    assert body == {"errors": ["Cannot upload files larger than 20.0 MB"]}


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
def test_audit_log_is_created_when_creating(service_api_client, attachments):
    data = {**VALID_DOCUMENT_DATA}
    if attachments:
        data["attachments"] = [
            SimpleUploadedFile(
                f"document{i}.pdf", b"file_content", content_type="application/pdf"
            )
            for i in range(attachments)
        ]

    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    ).json()

    assert Document.objects.count() == 1

    assert Attachment.objects.count() == attachments
    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id=response["id"],
            message__audit_event__operation="CREATE",
        ).count()
        == 1
    )
