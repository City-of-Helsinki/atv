from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response


def _get_error_wrapper(data) -> dict[str, list]:
    if not isinstance(data, list):
        data = [data]

    return {"errors": data}


def _get_error_detail(code, detail) -> dict[str, list]:
    return {"code": code.upper(), "message": detail}


def get_error_response(code, detail) -> dict[str, list]:
    return _get_error_wrapper(_get_error_detail(code.upper(), detail))


def sentry_before_send(event, hint):
    """
    Filter internal exceptions that should not be logged to Sentry
    https://docs.sentry.io/platforms/python/guides/django/configuration/filtering/
    """
    from atv.exceptions import ATVError

    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if isinstance(exc_value, ATVError):
            return None
    return event


def custom_exception_handler(exc, _context=None) -> Response:
    # Validation errors require a special processing to use the same format
    # as with the spec
    if isinstance(exc, ValidationError):
        response = Response(
            status=status.HTTP_400_BAD_REQUEST,
            data=_get_error_wrapper(
                list(  # TODO: Refactor this to produce cleaner error message for nested errors
                    _get_error_detail(
                        "INVALID_FIELD",
                        f"{k}: {v[0] if isinstance(v, list) else f'Required fields: {[key for key in v.keys()]}'}",
                    )
                    for k, v in exc.detail.items()
                )
            ),
        )
    elif isinstance(exc, APIException):
        # All APIException's detail are already in the code/message format,
        # so we just need to add the "error" wrapper
        response = Response(
            status=exc.status_code,
            data=_get_error_wrapper(exc.get_full_details()),
        )
    elif isinstance(exc, Http404):
        # Django handles 404 errors with a different error type, so it has to be handled
        # as a different case
        response = Response(
            status=status.HTTP_404_NOT_FOUND,
            data=get_error_response("NOT_FOUND", str(exc)),
        )
    else:
        # Generic error handler for the rest of cases
        response = Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            data=get_error_response(
                "GENERAL_ERROR",
                str(exc) or "Something went wrong, we don't know what.",
            ),
        )

    # Format the error codes so they're all in upper case
    for error in response.data.get("errors", []):
        try:
            error["code"] = error["code"].upper()
        except KeyError:
            # If for some reason the error message would have a different format
            # we just ignore it
            pass

    return response
