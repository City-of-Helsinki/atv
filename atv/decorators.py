from functools import wraps

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from atv.exceptions import MissingServiceAPIKey, ServiceNotIdentifiedError
from services.enums import ServicePermissions
from services.models import Service, ServiceAPIKey


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
    if not request.service:
        raise ServiceNotIdentifiedError("No service identified")


def _require_service_permission(permission_name):
    def permission_checker(request):
        if not request.user.is_superuser:
            try:
                _require_service(request)
            except ServiceNotIdentifiedError:
                raise PermissionDenied(
                    _("You do not have permission to perform this action.")
                )

        if not request.user.has_perm(permission_name, request.service):
            raise PermissionDenied(
                _("You do not have permission to perform this action.")
            )

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
        f"""Decorator that checks for {required_permission} permission."""

    return check_permission


def service_api_key_required():
    """
    Returns a decorator that checks if request includes a service API key to authorize it.
    If it includes one, it adds the related service to the `request.service`, otherwise it
    raises a NotAuthenticated error and returns 404.
    """

    def wrapper(function):
        @wraps(function)
        def service_setter(_viewset, request, *args, **kwargs):
            try:
                key = request.META.get(settings.API_KEY_CUSTOM_HEADER)
                if not key:
                    raise MissingServiceAPIKey()

                # get_from_key also checks that the key is still valid
                service_key = ServiceAPIKey.objects.get_from_key(key)
                service = service_key.service
                request.service = service
            except (
                ServiceAPIKey.DoesNotExist,
                Service.DoesNotExist,
                MissingServiceAPIKey,
            ):
                raise NotAuthenticated()

            return function(_viewset, request, *args, **kwargs)

        return service_setter

    return wrapper
