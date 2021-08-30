from rest_framework import serializers


class ATVError(Exception):
    """
    Request error that is not sent to Sentry.
    """


class ServiceNotIdentifiedError(ATVError):
    """The requester failed to identify the service they are coming from"""


class MissingServiceAPIKey(ATVError):
    """The request required a Service API Key but it was not present on the request"""


class ValidationError(serializers.ValidationError):
    def __init__(self, detail=None, code=None):
        if isinstance(detail, tuple):
            detail = {"errors": list(detail)}
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = {"errors": [detail]}

        super(ValidationError, self).__init__(detail, code)


def sentry_before_send(event, hint):
    """
    Filter internal exceptions that should not be logged to Sentry
    https://docs.sentry.io/platforms/python/guides/django/configuration/filtering/
    """
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if isinstance(exc_value, ATVError):
            return None
    return event
