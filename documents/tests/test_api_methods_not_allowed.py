from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.parametrize(
    "method,url",
    [
        ("PUT", reverse("documents-attachments-detail", args=[uuid4(), uuid4()])),
        ("PATCH", reverse("documents-attachments-detail", args=[uuid4(), uuid4()])),
        ("PUT", reverse("documents-detail", args=[uuid4()])),
    ],
)
def test_api_method_not_allowed(method, url, superuser_api_client):
    response = superuser_api_client.generic(method=method, path=url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
