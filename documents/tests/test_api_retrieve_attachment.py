import random
from uuid import uuid4

import pytest
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from audit_log.models import AuditLogEntry
from documents.tests.factories import AttachmentFactory
from services.enums import ServicePermissions
from services.tests.utils import get_user_service_client
from utils.exceptions import get_error_response


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


def test_retrieve_attachment_service_staff(user_factory, attachment):
    user = user_factory()
    group = GroupFactory()
    user.groups.add(group)
    assign_perm(
        ServicePermissions.VIEW_ATTACHMENTS.value, group, attachment.document.service
    )
    # Check that the owner of the document is different than the one
    # making the request
    assert attachment.document.user != user

    api_client = get_user_service_client(user, attachment.document.service)

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


def test_retrieve_attachment_owner(attachment):
    api_client = get_user_service_client(
        attachment.document.user, attachment.document.service
    )
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

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_retrieve_attachment_document_not_found(superuser_api_client):
    response = superuser_api_client.get(
        reverse("documents-attachments-detail", args=[uuid4(), random.randint(0, 100)])
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Attachment matches the given query.",
    )


def test_retrieve_attachment_attachment_not_found(superuser_api_client, document):
    response = superuser_api_client.get(
        reverse(
            "documents-attachments-detail", args=[document.id, random.randint(0, 100)]
        )
    )

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Attachment matches the given query.",
    )


@pytest.mark.parametrize(
    "ip_address", ["213.255.180.34", "2345:0425:2CA1::0567:5673:23b5"]
)
def test_audit_log_is_created_when_retrieving(user, service, ip_address):
    api_client = get_user_service_client(user, service)

    attachment = AttachmentFactory(
        document__draft=True,
        document__user=user,
        document__service=service,
    )

    api_client.get(
        reverse(
            "documents-attachments-detail",
            args=[attachment.document.id, attachment.id],
        ),
        HTTP_X_FORWARDED_FOR=ip_address,
    )

    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Attachment",
            message__audit_event__target__id=str(attachment.pk),
            message__audit_event__operation="READ",
            message__audit_event__target__lookup_field="pk",
            message__audit_event__target__endpoint="Attachment Instance",
            message__audit_event__actor__service=service.name,
            message__audit_event__actor__ip_address=ip_address,
        ).count()
        == 1
    )
