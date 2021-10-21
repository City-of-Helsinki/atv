from datetime import timezone
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from atv.tests.factories import GroupFactory
from audit_log.models import AuditLogEntry
from documents.models import Document
from documents.tests.factories import DocumentFactory
from services.enums import ServicePermissions
from services.tests.utils import get_user_service_client
from utils.exceptions import get_error_response

# OWNER-RELATED ACTIONS


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_owner(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        draft=True,
        user=user,
        service=service,
    )
    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_owner_someone_elses_document(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        draft=True,
        service=service,
    )
    assert Document.objects.count() == 1

    # Check that the owner of the document is different than the one
    # making the request
    assert document.user != user

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Document matches the given query.",
    )


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_owner_non_draft(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        draft=False,
        user=user,
        service=service,
    )

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        "Unable to modify document - it's no longer a draft",
    )


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_owner_after_lock_date(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(
        locked_after=today(timezone.utc) - relativedelta(days=1),
        draft=True,
        user=user,
        service=service,
    )

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        f"Unable to modify document - it's no longer a draft. Locked at: {document.locked_after}.",
    )


# STAFF-RELATED ACTION


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_staff(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        draft=True,
        service=service,
    )
    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0


@freeze_time("2021-06-30T12:00:00+03:00")
def test_destroy_document_staff_non_draft(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        service=service,
        draft=False,
    )

    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_staff_after_lock_date(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory(
        draft=True,
        locked_after=today(timezone.utc) - relativedelta(days=1),
        service=service,
    )

    assert Document.objects.count() == 1

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert body == get_error_response(
        "DOCUMENT_LOCKED",
        f"Unable to modify document - it's no longer a draft. Locked at: {document.locked_after}.",
    )


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_staff_another_service(user, service):
    api_client = get_user_service_client(user, service)

    group = GroupFactory()
    assign_perm(ServicePermissions.VIEW_DOCUMENTS.value, group, service)
    assign_perm(ServicePermissions.DELETE_DOCUMENTS.value, group, service)
    user.groups.add(group)

    document = DocumentFactory()

    response = api_client.delete(reverse("documents-detail", args=[document.id]))

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Document matches the given query.",
    )


# OTHER STUFF


@freeze_time("2021-06-30T12:00:00")
def test_destroy_document_not_found(superuser_api_client):
    response = superuser_api_client.delete(reverse("documents-detail", args=[uuid4()]))

    body = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert body == get_error_response(
        "NOT_FOUND",
        "No Document matches the given query.",
    )


def test_audit_log_is_created_when_destroying(user, service):
    api_client = get_user_service_client(user, service)

    document = DocumentFactory(draft=True, user=user, service=service)

    api_client.delete(reverse("documents-detail", args=[document.id]))

    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__target__type="Document",
            message__audit_event__target__id=str(document.pk),
            message__audit_event__operation="DELETE",
        ).count()
        == 1
    )
