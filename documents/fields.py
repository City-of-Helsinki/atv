from ast import literal_eval
from io import BytesIO

from Cryptodome.Cipher import AES
from django.db import models
from encrypted_fields.fields import EncryptedFieldMixin

from atv.settings import FIELD_ENCRYPTION_KEYS


class EncryptedJSONField(EncryptedFieldMixin, models.JSONField):
    def decrypt(self, value):
        text = super().decrypt(value)
        # Using literal_eval to get a dict from string, because json.loads() doesn't work here after django update
        return literal_eval(text)

    def encrypt(self, data_to_encrypt):
        # data_to_encrypt is Json string and .adapted is a dict like before update
        data_to_encrypt = data_to_encrypt.adapted
        # Dict is converted into a string which is then encrypted
        return super().encrypt(data_to_encrypt)


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
