from rest_framework import serializers


class ValidationError(serializers.ValidationError):
    def __init__(self, detail=None, code=None):
        if isinstance(detail, tuple):
            detail = {"errors": list(detail)}
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = {"errors": [detail]}

        super(ValidationError, self).__init__(detail, code)
