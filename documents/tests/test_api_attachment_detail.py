from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from documents.tests.factories import AttachmentFactory
from services.enums import ServicePermissions


def test_attachment_detail_service_user(api_client, user, attachment):
    group = GroupFactory(name=attachment.document.service.name)
    user.groups.add(group)
    assign_perm(
        ServicePermissions.VIEW_ATTACHMENTS.value, group, attachment.document.service
    )

    api_client.force_login(user=user)
    response = api_client.get(
        reverse(
            "documents-attachments-detail", args=[attachment.document.id, attachment.id]
        )
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    # The user should be able to see the attachment from the document
    assert body.get("id") == attachment.id


def test_attachment_detail_superuser(superuser_api_client, document):
    attachment = AttachmentFactory(document=document)

    response = superuser_api_client.get(
        reverse("documents-attachments-detail", args=[document.id, attachment.id])
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    # The user should be able to see the attachment from the document
    assert body.get("id") == attachment.id


def test_attachment_detail_no_service(api_client, user, attachment):
    api_client.force_login(user=user)
    response = api_client.get(
        reverse(
            "documents-attachments-detail", args=[attachment.document.id, attachment.id]
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
