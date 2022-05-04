import json

from django.db import models
from encrypted_fields.fields import EncryptedFieldMixin


class EncryptedJSONField(EncryptedFieldMixin, models.JSONField):
    def decrypt(self, value):
        text = super().decrypt(value)
        return json.loads(text)
