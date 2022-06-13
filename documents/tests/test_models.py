from uuid import uuid4

import pytest  # noqa
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import override_settings

from atv.exceptions import MaximumFileSizeExceededException

from ..models import Attachment, Document
from ..utils import get_decrypted_file
from .utils import generate_tos_uuid

User = get_user_model()


def test_content_is_encrypted(service, user):
    """Data stored in DB is actually encrypted."""
    field = Document._meta.get_field("content")
    content = {"field": "test_content"}

    document = Document.objects.create(
        service=service,
        user=user,
        content=content,
        business_id="1234567-8",
        transaction_id=str(uuid4()),
        tos_function_id=generate_tos_uuid(),
        tos_record_id=generate_tos_uuid(),
    )

    with connection.cursor() as cur:
        cur.execute("SELECT content FROM %s" % Document._meta.db_table)
        row = cur.fetchone()
        assert "test_content" not in row[0]

    data = field.decrypt(row[0])
    assert data == content
    assert document.content == data
    assert isinstance(document.content, dict)


@override_settings(MAX_FILE_SIZE=50)
def test_attachment_file_size_exceeded(document):
    with pytest.raises(MaximumFileSizeExceededException):
        Attachment.objects.create(
            document=document,
            file=SimpleUploadedFile(
                "document1.pdf",
                b"x" * 10000,
                content_type="application/pdf",
            ),
        )


def test_attachment_is_encrypted(document):
    """Data stored in DB is actually encrypted."""

    attachment = Attachment.objects.create(
        document=document,
        media_type="txt",
        file=SimpleUploadedFile(
            "document1.txt",
            b"this is testing text",
            content_type="text/plain",
        ),
    )

    file_content = attachment.file.read()
    assert b"this is testing text" not in file_content

    data = get_decrypted_file(file_content, "document.txt").read()
    assert data == b"this is testing text"


def test_model_str(document, attachment):
    assert str(document) == f"Document {document.id}"
    assert str(attachment) == f"Attachment {attachment.id}"
