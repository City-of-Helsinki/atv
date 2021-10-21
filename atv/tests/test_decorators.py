from unittest.mock import MagicMock

import pytest
from guardian.shortcuts import assign_perm
from helusers.authz import UserAuthorization
from rest_framework.exceptions import PermissionDenied

from atv.decorators import staff_required
from services.enums import ServicePermissions
from services.tests.factories import ServiceClientIdFactory, ServiceFactory
from users.tests.factories import UserFactory


@pytest.mark.parametrize("permission", list(ServicePermissions))
def test_staff_required(rf, permission):
    user = UserFactory()
    service = ServiceFactory()
    sc = ServiceClientIdFactory(service=service)

    request = rf.request()

    # The user is authenticated and has permissions for the service
    request.user = user
    request.auth = UserAuthorization(user, {"azp": sc.client_id})
    assign_perm(permission.value, user, service)

    wrapped_function = MagicMock()

    staff_required(permission)(wrapped_function)(None, request)

    wrapped_function.assert_called_once()
    assert request._service == service


def test_staff_required_invalid_permission(rf):
    wrapped_function = MagicMock()

    request = rf.request()
    with pytest.raises(ValueError) as exc:
        staff_required("invalid_perm")(wrapped_function)(None, request)

    assert (
        str(exc.value)
        == "Invalid required_permission given as argument: 'invalid_perm'"
    )

    wrapped_function.assert_not_called()
    assert not hasattr(request, "_service")


@pytest.mark.parametrize("permission", list(ServicePermissions))
def test_staff_required_user_is_not_staff(rf, permission):
    user = UserFactory()
    service = ServiceFactory()
    sc = ServiceClientIdFactory(service=service)

    request = rf.request()

    # The user is authenticated for the service but doesn't have the permissions
    request.user = user
    request.auth = UserAuthorization(user, {"azp": sc.client_id})

    wrapped_function = MagicMock()

    with pytest.raises(PermissionDenied):
        staff_required(permission)(wrapped_function)(None, request)

    wrapped_function.assert_not_called()
