import json
from io import BytesIO

from Crypto.Cipher import AES
from django.db import models
from encrypted_fields.fields import EncryptedFieldMixin

from atv.settings import FIELD_ENCRYPTION_KEYS


class EncryptedJSONField(EncryptedFieldMixin, models.JSONField):
    def decrypt(self, value):
        text = super().decrypt(value)
        return json.loads(text)

    def get_db_prep_save(self, value, connection):
        if self.empty_strings_allowed and value == bytes():
            value = ""
        # Instead of using db_prep_value use json.dumps() to get a json formatted object
        value = json.dumps(value)
        if value is not None:
            encrypted_value = self.encrypt(value)
            return connection.Database.Binary(encrypted_value)


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
