import uuid

from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from documents.tests.factories import DocumentFactory
from services.enums import ServicePermissions


@freeze_time("2020-06-01T00:00:00Z")
def test_list_document_service_user(api_client, user, service, snapshot):
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"
    expected_user_id = "66d0bfd0-308c-484d-aa22-301512899ae3"

    group = GroupFactory(name=service.name)
    user.groups.add(group)
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)

    document = DocumentFactory(
        id=expected_document_id,
        service=service,
        user__uuid=expected_user_id,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

    api_client.force_login(user=user)
    response = api_client.get(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body.pop("user_id") == str(expected_user_id)
    snapshot.assert_match(body)


@freeze_time("2020-06-01T00:00:00Z")
def test_retrieve_document_owner(api_client, user, service, snapshot):
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"

    group = GroupFactory(name=service.name)
    user.groups.add(group)

    document = DocumentFactory(
        id=expected_document_id,
        service=service,
        user=user,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

    api_client.force_login(user=user)
    response = api_client.get(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body.pop("user_id") == str(user.uuid)
    snapshot.assert_match(body)


@freeze_time("2020-06-01T00:00:00Z")
def test_list_document_superuser(superuser_api_client, snapshot):
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"
    expected_user_id = "66d0bfd0-308c-484d-aa22-301512899ae3"

    document = DocumentFactory(
        id=expected_document_id,
        user__uuid=expected_user_id,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

    response = superuser_api_client.get(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body.pop("user_id") == str(expected_user_id)
    snapshot.assert_match(body)


def test_list_document_no_permissions(api_client):
    response = api_client.get(reverse("documents-detail", args=[uuid.uuid4()]))

    body = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        body.get("detail", "") == "You do not have permission to perform this action."
    )
