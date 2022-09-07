from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from audit_log.enums import Role
from audit_log.models import AuditLogEntry
from documents.models import Attachment
from documents.tests.factories import DocumentFactory
from services.enums import ServicePermissions
from services.tests.utils import get_user_service_client
from utils.exceptions import get_error_response


@pytest.fixture
def document_data():
    return {
        "file": SimpleUploadedFile(
            "document1.pdf",
            b"file_content",
            content_type="application/pdf",
        )
    }


# OWNER-RELATED ACTIONS


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_and_retrieve_attachment(user, service, document_data, snapshot):
    api_client = get_user_service_client(user, service)
    document = DocumentFactory(
        id="5209bdd0-e626-4a7d-aa4d-73aaf961a93f",
        user=user,
        service=service,
        draft=True,
    )
    with mock.patch(
        "documents.serializers.attachment.virus_scan_attachment_file", return_value=None
    ):

        response = api_client.post(
            reverse("documents-attachments-list", args=[document.id]), document_data
        )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    attachment_id = body.pop("id")

    assert document.attachments.count() == 1
    assert document.attachments.first().id == attachment_id

    response = api_client.get(
        reverse("documents-attachments-detail", args=[document.id, attachment_id])
    )
    assert response.status_code == status.HTTP_200_OK

    snapshot.assert_match(body)


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_attachment_other_document(user, service):
    document = DocumentFactory(service=service)
    api_client = get_user_service_client(user, service)

    response = api_client.post(
        reverse("documents-attachments-list", args=[document.id]), {}
    )

    body = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Document matches the given query.",
    )


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_attachment_document_not_draft(user, service):
    document = DocumentFactory(
        id="5209bdd0-e626-4a7d-aa4d-73aaf961a93f",
        user=user,
        service=service,
        draft=False,
    )
    api_client = get_user_service_client(user, service)

    response = api_client.post(
        reverse("documents-attachments-list", args=[document.id]),
        {},
    )

    body = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        "Unable to modify document - it's no longer a draft",
    )


@freeze_time("2021-06-30T12:00:00+03:00")
def test_create_attachment_missing_document_id(user, service, document_data, snapshot):
    api_client = get_user_service_client(user, service)

    response = api_client.post(
        reverse("documents-attachments-list", args=[None]), document_data
    )

    body = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert body == get_error_response(
        "MISSING_PARAMETER",
        "Missing parameter: document_id.",
    )


@override_settings(MAX_FILE_SIZE=50)
def test_create_document_file_limit(user, service, snapshot, settings):
    api_client = get_user_service_client(user, service)
    document = DocumentFactory(
        id="5209bdd0-e626-4a7d-aa4d-73aaf961a93f",
        user=user,
        service=service,
        draft=True,
    )
    data = {
        "file": SimpleUploadedFile(
            "document1.pdf",
            b"x" * 10000,
            content_type="application/pdf",
        )
    }

    response = api_client.post(
        reverse("documents-attachments-list", args=[document.id]), data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Attachment.objects.count() == 0

    body = response.json()
    assert body == get_error_response(
        "MAXIMUM_FILE_SIZE_EXCEEDED",
        "Cannot upload files larger than 0.0 Mb: 0.01 Mb",
    )


# STAFF-RELATED ACTION


@freeze_time("2021-06-30T12:00:00+03:00")
@pytest.mark.parametrize("has_permission", [True, False])
def test_create_attachment_staff(
    user, service, document_data, snapshot, has_permission
):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.VIEW_ATTACHMENTS.value, group, service)
    if has_permission:
        assign_perm(ServicePermissions.ADD_ATTACHMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        id="5209bdd0-e626-4a7d-aa4d-73aaf961a93f",
        service=service,
        draft=True,
    )
    with mock.patch(
        "documents.serializers.attachment.virus_scan_attachment_file", return_value=None
    ):
        response = api_client.post(
            reverse("documents-attachments-list", args=[document.id]), document_data
        )

    if has_permission:
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        attachment_id = body.pop("id")
        assert document.attachments.count() == 1
        assert document.attachments.first().id == attachment_id
        snapshot.assert_match(body)
    else:
        body = response.json()
        assert document.attachments.count() == 0
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body == get_error_response(
            "PERMISSION_DENIED",
            "You do not have permission to perform this action.",
        )


# OTHER STUFF


@pytest.mark.parametrize(
    "ip_address", ["213.255.180.34", "2345:0425:2CA1::0567:5673:23b5"]
)
def test_audit_log_is_created_when_creating(
    user, service, document_data, snapshot, ip_address
):
    api_client = get_user_service_client(user, service)
    document = DocumentFactory(
        id="5209bdd0-e626-4a7d-aa4d-73aaf961a93f",
        user=user,
        service=service,
        draft=True,
    )
    with mock.patch(
        "documents.serializers.attachment.virus_scan_attachment_file", return_value=None
    ):
        response = api_client.post(
            reverse("documents-attachments-list", args=[document.id]),
            document_data,
            HTTP_X_FORWARDED_FOR=ip_address,
        ).json()

    assert document.attachments.count() == 1
    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Attachment",
            message__audit_event__target__id=str(response["id"]),
            message__audit_event__operation="CREATE",
            message__audit_event__actor__service=service.name,
            message__audit_event__actor__role=Role.USER,
            message__audit_event__actor__ip_address=ip_address,
        ).count()
        == 1
    )
