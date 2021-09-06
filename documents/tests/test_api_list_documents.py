from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from documents.tests.factories import DocumentFactory
from services.enums import ServicePermissions
from services.tests.factories import ServiceFactory


def test_list_document_service_user(api_client, user):
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"
    service1 = ServiceFactory(name="service-1")
    service2 = ServiceFactory(name="service-2")

    group = GroupFactory(name=service1.name)
    user.groups.add(group)
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service1)

    DocumentFactory(id=expected_document_id, service=service1)
    DocumentFactory(service=service2)

    api_client.force_login(user=user)
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    # The user should only be able to see the one document from the service 1
    assert len(body) == 1
    assert body[0].get("id") == expected_document_id


def test_list_document_superuser(api_client, superuser_api_client):
    service1 = ServiceFactory(name="service-1")
    service2 = ServiceFactory(name="service-2")

    DocumentFactory(
        service=service1,
        id="ffd80e3d-07d7-42db-ba58-b4c4ede2bc0d",
    )
    DocumentFactory(
        service=service2,
        id="8ce91dde-b7ba-4e20-8dd0-835d2060c9d3",
    )

    response = superuser_api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    # The superuser should be able to see all the documents
    assert len(body) == 2


def test_list_document_no_service(api_client, user):
    api_client.force_login(user=user)
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
