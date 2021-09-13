import random
from uuid import uuid4

from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from services.enums import ServicePermissions


def test_retrieve_attachment_superuser(superuser_api_client, attachment):
    response = superuser_api_client.get(
        reverse(
            "documents-attachments-detail", args=[attachment.document.id, attachment.id]
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.getvalue() == b"Test file"
    assert response.headers.get("Content-Type") == "text/plain"
    assert response.headers.get(
        "Content-Disposition"
    ) == 'attachment; filename="{}"'.format(attachment.filename)


def test_retrieve_attachment_service_staff(api_client, attachment):
    group = GroupFactory(name=attachment.document.service.name)
    attachment.document.user.groups.add(group)
    assign_perm(
        ServicePermissions.VIEW_DOCUMENTS.value, group, attachment.document.service
    )

    api_client.force_login(user=attachment.document.user)

    response = api_client.get(
        reverse(
            "documents-attachments-detail", args=[attachment.document.id, attachment.id]
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.getvalue() == b"Test file"
    assert response.headers.get("Content-Type") == "text/plain"
    assert response.headers.get(
        "Content-Disposition"
    ) == 'attachment; filename="{}"'.format(attachment.filename)


def test_retrieve_attachment_owner(api_client, attachment):
    api_client.force_login(user=attachment.document.user)

    response = api_client.get(
        reverse(
            "documents-attachments-detail", args=[attachment.document.id, attachment.id]
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.getvalue() == b"Test file"
    assert response.headers.get("Content-Type") == "text/plain"
    assert response.headers.get(
        "Content-Disposition"
    ) == 'attachment; filename="{}"'.format(attachment.filename)


def test_retrieve_attachment_no_permissions(api_client, attachment):
    response = api_client.get(
        reverse(
            "documents-attachments-detail", args=[attachment.document.id, attachment.id]
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_attachment_document_not_found(superuser_api_client):
    response = superuser_api_client.get(
        reverse("documents-attachments-detail", args=[uuid4(), random.randint(0, 100)])
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body.get("detail", "") == "Not found."


def test_retrieve_attachment_attachment_not_found(superuser_api_client, document):
    response = superuser_api_client.get(
        reverse(
            "documents-attachments-detail", args=[document.id, random.randint(0, 100)]
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body.get("detail", "") == "Not found."
