import ast
from uuid import uuid4

import pytest  # noqa
from django.contrib.auth import get_user_model
from django.db import connection

from ..models import Document
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
    assert data == str(content)
    assert document.content == ast.literal_eval(data)
    assert isinstance(document.content, dict)
