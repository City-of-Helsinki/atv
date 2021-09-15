from django.conf import settings
from django.urls import reverse
from rest_framework import status

from ..models import ServiceAPIKey
from .factories import ServiceFactory


def get_api_key():
    service = ServiceFactory()
    api_key, key = ServiceAPIKey.objects.create_key(name="APIKey", service=service)
    return key


def test_anonymous_user_cannot_get_documents_api_with_an_api_key(api_client):
    key = get_api_key()

    api_client.credentials(**{settings.API_KEY_CUSTOM_HEADER: key})
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_post_documents_api_with_a_wrong_api_key(api_client):
    key = get_api_key()

    api_client.credentials(**{settings.API_KEY_CUSTOM_HEADER: key[::-1]})
    response = api_client.post(reverse("documents-list"), {"data": "ok"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_anonymous_user_cannot_post_documents_api_without_an_api_key(api_client):
    response = api_client.post(reverse("documents-list"), {"data": "ok"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
