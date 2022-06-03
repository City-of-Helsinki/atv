from django.conf import settings
from pyclamd import pyclamd

from atv.exceptions import MaliciousFileException


def get_attachment_file_path(instance, filename):
    """File will be uploaded to MEDIA_ROOT/ATTACHMENT_MEDIA_DIR/<document_id>/<filename>"""
    return f"{settings.ATTACHMENT_MEDIA_DIR}/{instance.document.id}/{filename}"


def get_document_attachment_directory_path(instance):
    """Get the root directory for a document's attachments.

    :type instance: documents.models.Document
    """
    return f"{settings.ATTACHMENT_MEDIA_DIR}/{instance.id}/"


# TODO: Consider scanning files on download as well to improve chance of catching most recent threats to protect users
#   if clamav virus databases didn't include the virus' profile at the time of upload
# Note this function is mocked in testing because there is no clamav connection during pipeline testing
def virus_scan_attachment_file(file_data):
    cd = pyclamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST)
    if cd.scan_stream(file_data) is not None:
        raise MaliciousFileException
