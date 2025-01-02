import freezegun
import pytest
from dateutil.parser import isoparse
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from audit_log.models import AuditLogEntry
from documents.models import Document
from documents.tests.factories import DocumentFactory
from documents.tests.test_api_create_document import VALID_DOCUMENT_DATA
from services.enums import ServicePermissions
from services.tests.factories import ServiceFactory
from services.tests.utils import get_user_service_client
from users.tests.factories import UserFactory


def test_list_document_service_admin_user(user):
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"
    service1 = ServiceFactory(name="service-1")
    service2 = ServiceFactory(name="service-2")

    group = GroupFactory()
    user.groups.add(group)
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service1)

    DocumentFactory(id=expected_document_id, service=service1)
    DocumentFactory(service=service2)

    api_client = get_user_service_client(user, service1)
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    results = body.get("results", [])

    # The user should only be able to see the one document from the service 1
    assert body.get("count") == 1
    assert len(results) == 1
    assert results[0].get("id") == expected_document_id


def test_list_document_superuser(superuser_api_client):
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


def test_list_document_owner(user, service):
    api_client = get_user_service_client(user, service)
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"

    DocumentFactory(id=expected_document_id, service=service, user=user)
    DocumentFactory(service=service)

    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    results = body.get("results", [])

    # The user should only be able to see the one document from the service 1
    assert body.get("count") == 1
    assert len(results) == 1
    assert results[0].get("id") == expected_document_id


def test_list_document_owner_only_authenticated_service(user, service):
    api_client = get_user_service_client(user, service)
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"

    DocumentFactory(id=expected_document_id, service=service, user=user)
    # Document for the same user but different service
    DocumentFactory(user=user)

    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    results = body.get("results", [])

    # The user should only be able to see the one document from the service 1
    assert body.get("count") == 1
    assert len(results) == 1
    assert results[0].get("id") == expected_document_id


def test_list_document_no_service(api_client, user):
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_document_anonymous_user(api_client):
    response = api_client.get(reverse("documents-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_gdpr_api_list_service_api_key(user, service_api_client):
    data = {**VALID_DOCUMENT_DATA, "user_id": user.uuid, "deletable": True}
    other_service = ServiceFactory()
    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )
    assert response.status_code == status.HTTP_201_CREATED
    data["deletable"] = False
    response = service_api_client.post(
        reverse("documents-list"), data, format="multipart"
    )
    assert response.status_code == status.HTTP_201_CREATED
    DocumentFactory(service=other_service, user=user, deletable=False)

    assert Document.objects.count() == 3

    response = service_api_client.get(reverse("gdpr-api-detail", args=[user.uuid]))

    assert response.status_code == status.HTTP_200_OK
    body = response.data
    assert body["data"]["total_deletable"] == 1
    assert body["data"]["total_undeletable"] == 1


def test_gdpr_api_list_anonymous(api_client, user, service):
    other_service = ServiceFactory()
    other_user = UserFactory()
    DocumentFactory(service=service, user=user, deletable=True)
    DocumentFactory(service=other_service, user=user, deletable=False)
    DocumentFactory(service=other_service, user=other_user, deletable=False)

    assert Document.objects.count() == 3

    response = api_client.get(reverse("gdpr-api-detail", args=[user.uuid]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_gdpr_api_list_user(user, service):
    api_client = get_user_service_client(user, service)
    other_service = ServiceFactory()
    other_user = UserFactory()
    DocumentFactory(service=service, user=user, deletable=True)
    DocumentFactory(service=other_service, user=user, deletable=False)
    DocumentFactory(service=other_service, user=other_user, deletable=False)

    assert Document.objects.count() == 3

    response = api_client.get(reverse("gdpr-api-detail", args=[user.uuid]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_document_batch_list_service_api_key(service_api_client, user):
    data = {**VALID_DOCUMENT_DATA, "user_id": user.uuid}
    other_service = ServiceFactory()
    document_ids = []
    for _i in range(2):
        response = service_api_client.post(
            reverse("documents-list"), data, format="multipart"
        )
        assert response.status_code == status.HTTP_201_CREATED
        document_ids.append(response.json()["id"])

    other_document_id = DocumentFactory(service=other_service, user=user).id

    assert Document.objects.count() == 3
    response = service_api_client.post(
        reverse("documents-batch-list"),
        data={"document_ids": document_ids},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    response_ids = [x["id"] for x in response.json()]
    assert len(response_ids) == 2
    assert str(other_document_id) not in response_ids


def test_document_batch_list_user(user, service):
    api_client = get_user_service_client(user, service)
    other_service = ServiceFactory()
    other_user = UserFactory()
    d1 = DocumentFactory(service=service, user=user, deletable=True)
    d2 = DocumentFactory(service=other_service, user=user, deletable=False)
    d3 = DocumentFactory(service=other_service, user=other_user, deletable=False)

    assert Document.objects.count() == 3

    response = api_client.post(
        reverse("documents-batch-list"),
        data={"document_ids": [d1.id, d2.id, d3.id]},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    response_ids = [x["id"] for x in response.json()]
    assert len(response_ids) == 1
    assert [str(d1.id)] == response_ids


@pytest.mark.parametrize(
    "param,value",
    [
        ("status", "processed"),
        ("type", "application"),
        ("business_id", "1234567-8"),
        ("transaction_id", "49bee2d108be4a68a79d2e5e85791ec8"),
        ("lookfor", "test:search, search:test"),
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
        metadata={"test": "search", "search": "test"},
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
    assert body.get("status").get("value") == "processed" == str(document.status)
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


def test_list_document_filter_user_id(superuser_api_client):
    document = DocumentFactory(
        id="8ce91dde-b7ba-4e20-8dd0-835d2060c9d3",
        user=None,
    )
    document1 = DocumentFactory(
        id="ffd80e3d-07d7-42db-ba58-b4c4ede2bc0d",
        user__uuid="66d0bfd0-308c-484d-aa22-301512899ae3",
    )

    url = f"{reverse('documents-list')}?user_id=null"
    response = superuser_api_client.get(url)
    results = response.json().get("results", [])

    assert len(results) == 1
    body = results[0]
    assert body.get("id") == "8ce91dde-b7ba-4e20-8dd0-835d2060c9d3" == str(document.id)

    url = f"{reverse('documents-list')}?user_id=66d0bfd0-308c-484d-aa22-301512899ae3"
    response = superuser_api_client.get(url)
    results = response.json().get("results", [])

    assert len(results) == 1
    body = results[0]
    assert body.get("id") == "ffd80e3d-07d7-42db-ba58-b4c4ede2bc0d" == str(document1.id)

    url = reverse("documents-list")
    response = superuser_api_client.get(url)
    results = response.json().get("results", [])

    assert len(results) == 2

    url = f"{reverse('documents-list')}?user_id=NotValidUUID"
    response = superuser_api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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


def test_list_document_statistics_service_staff(service_api_client, user):
    response = service_api_client.post(
        reverse("documents-list"), VALID_DOCUMENT_DATA, format="multipart"
    )
    assert response.status_code == status.HTTP_201_CREATED
    service = response.json()["service"]

    other_user = UserFactory()
    other_service = ServiceFactory()
    DocumentFactory(service=other_service, user=user, deletable=False)
    DocumentFactory(service=other_service, user=other_user, deletable=False)

    response = service_api_client.get(reverse("document-statistics-list"))
    assert response.status_code == status.HTTP_200_OK
    assert all(
        [document["service"] == service for document in response.json()["results"]]
    )


def test_list_document_statistics_stats_permission(service, user):
    other_user = UserFactory()
    other_service = ServiceFactory()
    group = GroupFactory()
    assign_perm("users.view_document_statistics", group)
    DocumentFactory(service=service, user=user, deletable=True)
    DocumentFactory(service=service, user=other_user, deletable=True)
    DocumentFactory(service=other_service, user=user, deletable=False)
    DocumentFactory(service=other_service, user=other_user, deletable=False)

    user.groups.add(group)
    api_client = get_user_service_client(user, service)
    response = api_client.get(reverse("document-statistics-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 4


def test_list_document_statistics_user(service, user):
    api_client = get_user_service_client(user, service)
    response = api_client.get(reverse("document-statistics-list"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "ip_address", ["213.255.180.34", "2345:0425:2CA1::0567:5673:23b5"]
)
def test_audit_log_is_created_when_listing(user, ip_address):
    service = ServiceFactory()
    group = GroupFactory()
    user.groups.add(group)
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    DocumentFactory.create_batch(2, service=service)

    api_client = get_user_service_client(user, service)
    response = api_client.get(
        reverse("documents-list"), HTTP_X_FORWARDED_FOR=ip_address
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id="",
            message__audit_event__target__endpoint="Document List",
            message__audit_event__operation="READ",
            message__audit_event__actor__service=service.name,
            message__audit_event__actor__ip_address=ip_address,
        ).count()
        == 1
    )
