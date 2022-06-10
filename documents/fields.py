import json
from io import BytesIO

from Cryptodome.Cipher import AES
from django.db import models
from encrypted_fields.fields import EncryptedFieldMixin

from atv.settings import FIELD_ENCRYPTION_KEYS


class EncryptedJSONField(EncryptedFieldMixin, models.JSONField):
    def decrypt(self, value):
        text = super().decrypt(value)
        return json.loads(text)


class EncryptedFileField(models.FileField):
    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, self.encrypt_file(file.file), save=False)
        return file

    @staticmethod
    def encrypt_file(file):
        data_to_encrypt = file.read()
        cipher = AES.new(bytes.fromhex(FIELD_ENCRYPTION_KEYS[0]), AES.MODE_GCM)
        nonce = cipher.nonce
        cypher_text, tag = cipher.encrypt_and_digest(data_to_encrypt)
        return BytesIO(nonce + tag + cypher_text)
