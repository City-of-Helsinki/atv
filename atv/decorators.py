from functools import wraps

from rest_framework.exceptions import MethodNotAllowed, PermissionDenied

from services.enums import ServicePermissions
from services.utils import get_service_from_request


def _use_request_tests(*test_funcs):
    def decorator(decorator_function):
        @wraps(decorator_function)
        def wrapper(function):
            @wraps(function)
            def request_tester(viewset, request, *args, **kwargs):
                for test_func in test_funcs:
                    test_func(request)

                return function(viewset, request, *args, **kwargs)

            return request_tester

        return wrapper

    return decorator


def _require_service(request):
    service = get_service_from_request(request, raise_exception=False)

    if not request.user.is_superuser and not service:
        raise PermissionDenied()


def _require_service_permission(permission_name):
    def permission_checker(request):
        _require_service(request)

        if not request.user.has_perm(
            permission_name,
            get_service_from_request(request),
        ):
            raise PermissionDenied()

    return permission_checker


def staff_required(required_permission=ServicePermissions.VIEW_DOCUMENTS):
    """
    Returns a decorator that checks if the user has staff permission on resources for the service
    specified in the request. Required permission can be defined as an argument, defaults to 'view'.
    """

    if not isinstance(required_permission, ServicePermissions):
        raise ValueError(
            f"Invalid required_permission given as argument: '{required_permission}'"
        )

    @_use_request_tests(_require_service_permission(required_permission.value))
    def check_permission():
        """Decorator that checks for required permission."""

    return check_permission


def not_allowed():
    def wrapper(function):
        @wraps(function)
        def raise_exc(_viewset, request, *args, **kwargs):
            raise MethodNotAllowed(request.method)

        return raise_exc

    return wrapper


def service_required():
    @_use_request_tests(_require_service)
    def check_permission():
        """Decorator for checking that the service is present in the request"""

    return check_permission
