import freezegun
import pytest
from dateutil.parser import isoparse
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from audit_log.models import AuditLogEntry
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

    results = body.get("results", [])

    # The user should only be able to see the one document from the service 1
    assert body.get("count") == 1
    assert len(results) == 1
    assert results[0].get("id") == expected_document_id


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

    results = body.get("results", [])

    # The superuser should be able to see all the documents
    assert body.get("count") == 2
    assert len(results) == 2


def test_list_document_no_service(api_client, user):
    api_client.force_login(user=user)
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "param,value",
    [
        ("status", "processed"),
        ("type", "application"),
        ("business_id", "1234567-8"),
        ("user_id", "65352f2c-7b35-4c0d-8209-1d685f30cce9"),
        ("transaction_id", "49bee2d108be4a68a79d2e5e85791ec8"),
    ],
)
def test_list_document_filter(superuser_api_client, service, param, value):
    document = DocumentFactory(
        service=service,
        id="ffd80e3d-07d7-42db-ba58-b4c4ede2bc0d",
        status="processed",
        type="application",
        business_id="1234567-8",
        transaction_id="49bee2d108be4a68a79d2e5e85791ec8",
        user__uuid="65352f2c-7b35-4c0d-8209-1d685f30cce9",
    )
    DocumentFactory(
        service=service,
        id="8ce91dde-b7ba-4e20-8dd0-835d2060c9d3",
        status="pending",
        type="rejection",
        business_id="8765432-1",
        transaction_id="cdf67421223b417c90c23b2a4f830286",
        user__uuid="66d0bfd0-308c-484d-aa22-301512899ae3",
    )

    url = f"{reverse('documents-list')}?{param}={value}"
    response = superuser_api_client.get(url)

    results = response.json().get("results", [])

    assert len(results) == 1
    body = results[0]

    assert body.get("id") == "ffd80e3d-07d7-42db-ba58-b4c4ede2bc0d" == str(document.id)
    assert body.get("status") == "processed" == str(document.status)
    assert body.get("type") == "application" == str(document.type)
    assert body.get("business_id") == "1234567-8" == str(document.business_id)
    assert (
        body.get("transaction_id")
        == "49bee2d108be4a68a79d2e5e85791ec8"
        == str(document.transaction_id)
    )
    assert (
        body.get("user_id")
        == "65352f2c-7b35-4c0d-8209-1d685f30cce9"
        == str(document.user.uuid)
    )


@pytest.mark.parametrize(
    "ordering",
    [
        "created_at",
        "-created_at",
        "updated_at",
        "-updated_at",
    ],
)
def test_list_document_sorting(superuser_api_client, ordering):
    with freezegun.freeze_time("2021-01-30T12:00:00+03:00"):
        DocumentFactory()

    with freezegun.freeze_time("2021-06-30T12:00:00+03:00"):
        DocumentFactory()

    url = f"{reverse('documents-list')}?sort={ordering}"
    response = superuser_api_client.get(url)

    results = response.json().get("results", [])

    assert len(results) == 2

    document_1 = results[0]
    document_2 = results[1]

    if ordering == "created_at":
        assert isoparse(document_1.get("created_at")) < isoparse(
            document_2.get("created_at")
        )
    elif ordering == "-created_at":
        assert isoparse(document_2.get("created_at")) < isoparse(
            document_1.get("created_at")
        )
    if ordering == "updated_at":
        assert isoparse(document_1.get("updated_at")) < isoparse(
            document_2.get("updated_at")
        )
    elif ordering == "-updated_at":
        assert isoparse(document_2.get("updated_at")) < isoparse(
            document_1.get("updated_at")
        )


@pytest.mark.parametrize(
    "filter_field,field,expected",
    [
        ("created_before", "created_at", "2021-01-30T12:00:00+03:00"),
        ("created_after", "created_at", "2021-06-30T12:00:00+03:00"),
        ("updated_before", "updated_at", "2021-01-30T12:00:00+03:00"),
        ("updated_after", "updated_at", "2021-06-30T12:00:00+03:00"),
    ],
)
def test_list_document_filter_created_at_range(
    superuser_api_client, filter_field, field, expected
):
    with freezegun.freeze_time("2021-01-30T12:00:00+03:00"):
        DocumentFactory()

    with freezegun.freeze_time("2021-06-30T12:00:00+03:00"):
        DocumentFactory()

    url = f"{reverse('documents-list')}?{filter_field}=2021-03-01"
    response = superuser_api_client.get(url)

    results = response.json().get("results", [])

    assert len(results) == 1

    document = results[0]
    assert isoparse(document.get(field)) == isoparse(expected)


def test_audit_log_is_created_when_listing(api_client, user):
    service = ServiceFactory()
    group = GroupFactory(name=service.name)
    user.groups.add(group)
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    DocumentFactory.create_batch(2, service=service)

    api_client.force_login(user=user)
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_200_OK
    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id="",
            message__audit_event__operation="READ",
        ).count()
        == 1
    )
