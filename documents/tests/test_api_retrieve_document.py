import uuid

from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from documents.tests.factories import DocumentFactory
from services.enums import ServicePermissions
from services.tests.factories import ServiceFactory
from services.tests.utils import get_user_service_client
from users.tests.factories import UserFactory
from utils.exceptions import get_error_response


@freeze_time("2020-06-01T00:00:00Z")
def test_list_document_service_user(user, service, snapshot):
    api_client = get_user_service_client(user, service)
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"
    expected_user_id = "66d0bfd0-308c-484d-aa22-301512899ae3"

    group = GroupFactory()
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

    response = api_client.get(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body.pop("user_id") == str(expected_user_id)
    snapshot.assert_match(body)


@freeze_time("2020-06-01T00:00:00Z")
def test_retrieve_document_owner(user, service, snapshot):
    api_client = get_user_service_client(user, service)
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"

    group = GroupFactory()
    user.groups.add(group)

    document = DocumentFactory(
        id=expected_document_id,
        service=service,
        user=user,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

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
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert body == get_error_response(
        "NOT_AUTHENTICATED",
        "Authentication credentials were not provided.",
    )


def test_get_user_document_metadatas_superuser(superuser_api_client):
    expected_document_id = "485af718-d9d1-46b9-ad7b-33ea054126e3"
    expected_user_id = "66d0bfd0-308c-484d-aa22-301512899ae3"

    DocumentFactory(
        id=expected_document_id,
        user__uuid=expected_user_id,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

    response = superuser_api_client.get(
        reverse("userdocuments-detail", args=[expected_user_id])
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json().get("count") == 1


def test_get_user_document_metadatas_service_api_key(user, service_api_client):
    service = ServiceFactory()
    other_service = ServiceFactory()

    DocumentFactory(
        id="485af718-d9d1-46b9-ad7b-33ea054126e3",
        user=user,
        service=service,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )
    DocumentFactory(
        id="585af718-d9d1-46b9-ad7b-33ea054126e3",
        user=user,
        service=other_service,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

    response = service_api_client.get(reverse("userdocuments-detail", args=[user.uuid]))
    assert response.status_code == status.HTTP_200_OK

    assert response.json().get("count") == 2


def test_get_user_document_metadatas_user(user, service):
    api_client = get_user_service_client(user, service)

    DocumentFactory(
        id="485af718-d9d1-46b9-ad7b-33ea054126e3",
        user=user,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

    response = api_client.get(reverse("userdocuments-detail", args=[user.uuid]))

    assert response.status_code == status.HTTP_200_OK

    assert response.json().get("count") == 1


def test_get_user_document_metadatas_wrong_user(user, service):
    api_client = get_user_service_client(user, service)

    other_user = UserFactory()
    DocumentFactory(
        id="485af718-d9d1-46b9-ad7b-33ea054126e3",
        user=other_user,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c",
    )

    response = api_client.get(reverse("userdocuments-detail", args=[other_user.uuid]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_document_metadatas_user_doesnt_exist(service_api_client):
    response = service_api_client.get(
        reverse("userdocuments-detail", args=["bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c"])
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_document_metadatas_anonymous_user(api_client):

    response = api_client.get(
        reverse("userdocuments-detail", args=["bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c"])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_document_metadatas_filtering_user(user, service):
    api_client = get_user_service_client(user, service)
    transaction_id = "bd3fd958-cfeb-4ab1-bea4-5c058e8fee5c"
    DocumentFactory(
        id="485af718-d9d1-46b9-ad7b-33ea054126e3",
        user=user,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id=transaction_id,
    )
    DocumentFactory(
        id="485af718-d9d1-46b9-ad7b-33ea054126e4",
        user=user,
        tos_function_id="81eee139736f4e52b046a1b27211c202",
        tos_record_id="0f499febb6414e1dafc93febca5ef312",
        transaction_id="bd3fd958-cfeb-4ab1-bea4-5c058e8fee5f",
    )

    response = api_client.get(
        reverse("userdocuments-detail", args=[user.uuid])
        + f"?transaction_id={transaction_id}"
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json().get("count") == 1
