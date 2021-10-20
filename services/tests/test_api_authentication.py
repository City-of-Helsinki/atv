from django.conf import settings
from django.urls import reverse
from guardian.shortcuts import remove_perm
from rest_framework import status

from ..enums import ServicePermissions
from ..models import ServiceAPIKey
from .factories import ServiceFactory


def get_api_key():
    service = ServiceFactory()
    api_key, key = ServiceAPIKey.objects.create_key(name="APIKey", service=service)
    return api_key, key


def test_service_api_key_can_list_documents(api_client):
    api_key, key = get_api_key()

    api_client.credentials(**{settings.API_KEY_CUSTOM_HEADER: key})
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_200_OK


def test_service_api_key_cannot_get_documents_without_permissions(api_client):
    api_key, key = get_api_key()
    # All permissions are assigned to a newly created ServiceAPIKey
    remove_perm(ServicePermissions.VIEW_DOCUMENTS, api_key.user, api_key.service)

    api_client.credentials(**{settings.API_KEY_CUSTOM_HEADER: key})
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_service_api_key_needs_to_be_correct_for_auth(api_client):
    api_key, key = get_api_key()

    api_client.credentials(**{settings.API_KEY_CUSTOM_HEADER: key[::-1]})
    response = api_client.post(reverse("documents-list"), {"data": "ok"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authentication_is_required(api_client):
    response = api_client.post(reverse("documents-list"), {"data": "ok"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
