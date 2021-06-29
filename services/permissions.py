from typing import Any

from django.http import HttpRequest
from rest_framework_api_key.permissions import BaseHasAPIKey

from .models import ServiceAPIKey


class HasServiceAPIKey(BaseHasAPIKey):
    """The ServiceAPIKey only allows for creating Documents for anonymous users.
    If the requirements regarding API Keys change, this permission set has to be changed.
    """

    model = ServiceAPIKey

    def has_permission(self, request: HttpRequest, view: Any) -> bool:
        if request.method not in ("POST", "HEAD", "OPTIONS"):
            return False

        return super(HasServiceAPIKey, self).has_permission(request, view)
