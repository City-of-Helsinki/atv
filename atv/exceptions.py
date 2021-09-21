from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

from utils.files import b_to_mb


class ATVError(Exception):
    """
    Request error that is not sent to Sentry.
    """


class ServiceNotIdentifiedError(ATVError):
    """The requester failed to identify the service they are coming from"""


class MissingServiceAPIKey(ATVError):
    """The request required a Service API Key but it was not present on the request"""


class MaximumFileCountExceededException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "MAXIMUM_FILE_COUNT_EXCEEDED"
    default_detail = (
        _("File upload is limited to {max_file_upload_allowed}").format(
            max_file_upload_allowed=settings.MAX_FILE_UPLOAD_ALLOWED
        ),
    )


class MaximumFileSizeExceededException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "MAXIMUM_FILE_SIZE_EXCEEDED"
    default_detail = _("Cannot upload files larger than {size_mb} Mb")

    def __init__(self, detail=None, code=None, file_size=None):
        detail = detail or self.default_detail.format(
            size_mb=b_to_mb(settings.MAX_FILE_SIZE)
        )
        if file_size:
            detail = f"{detail}: {file_size} Mb"

        super().__init__(detail=detail, code=code or self.default_code)


class DocumentLockedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "DOCUMENT_LOCKED"
    default_detail = _("Unable to modify document - it's no longer a draft.")

    def __init__(self, detail=None, code=None, locked_after=None):
        detail = detail or self.default_detail
        if locked_after:
            detail = f"{detail} Locked at: {locked_after}."

        super().__init__(detail=detail, code=code or self.default_code)


class InvalidFieldException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "INVALID_FIELD"
    default_detail = _("Got invalid input fields")
