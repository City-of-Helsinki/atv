from io import BytesIO

from Cryptodome.Cipher import AES
from django.conf import settings
from django.core.files import File
from pyclamd import pyclamd

from atv.exceptions import MaliciousFileException
from atv.settings import FIELD_ENCRYPTION_KEYS


def get_attachment_file_path(instance, filename):
    """File will be uploaded to MEDIA_ROOT/ATTACHMENT_MEDIA_DIR/<document_id>/<filename>"""
    return f"{settings.ATTACHMENT_MEDIA_DIR}/{instance.document.id}/{filename}"


def get_document_attachment_directory_path(instance):
    """Get the root directory for a document's attachments.

    :type instance: documents.models.Document
    """
    return f"{settings.ATTACHMENT_MEDIA_DIR}/{instance.id}/"


def get_decrypted_file(file, file_name):
    nonce = file[:16]
    # Perform same nonce checks here as Pycryptodome, so we can raise a more user
    # friendly error message
    if not isinstance(nonce, (bytes, bytearray, memoryview)) or len(nonce) != 16:
        raise ValueError("Data is corrupted.")
    tag = file[16:32]
    cypher_text = file[32:]
    counter = 0
    num_keys = len(FIELD_ENCRYPTION_KEYS)
    while counter < num_keys:
        cipher = AES.new(
            bytes.fromhex(FIELD_ENCRYPTION_KEYS[counter]), AES.MODE_GCM, nonce=nonce
        )
        try:
            plaintext = cipher.decrypt_and_verify(cypher_text, tag)
        except ValueError:
            counter += 1
            continue
        return File(BytesIO(plaintext), name=file_name)
    raise ValueError("AES Key incorrect or data is corrupted")


# TODO: Consider scanning files on download as well to improve chance of catching most recent threats to protect users
#   if clamav virus databases didn't include the virus' profile at the time of upload
# Note this function is mocked in testing because there is no clamav connection during pipeline testing
def virus_scan_attachment_file(file_data):
    cd = pyclamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST)
    if cd.scan_stream(file_data) is not None:
        raise MaliciousFileException
