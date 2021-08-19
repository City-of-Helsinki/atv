import json
import uuid
from unittest.mock import patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from documents.models import Attachment, Document

VALID_DOCUMENT_DATA = {
    "status": "handled",
    "type": "mysterious form",
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "business_id": "1234567-8",
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "metadata": json.dumps({"created_by": "alex", "testing": True}),
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
    with patch.object(
        Document._meta.get_field("id"),
        "default",
        new=lambda: uuid.UUID("2d2b7a36-a306-4e35-990f-13aea04263ff"),
    ):
        response = service_api_client.post(
            reverse("documents-list"), data, format="multipart"
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert Document.objects.count() == 1
    assert Attachment.objects.count() == 2

    document = Document.objects.first()
    assert document.attachments.count() == 2

    body = response.json()
    snapshot.assert_match(body)


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

    document = Document.objects.first()
    assert document.attachments.count() == 0

    body = response.json()

    assert body.get("attachments") == []
