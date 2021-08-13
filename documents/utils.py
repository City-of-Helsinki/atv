from django.conf import settings


def get_attachment_file_path(instance, filename):
    """File will be uploaded to MEDIA_ROOT/ATTACHMENT_MEDIA_DIR/<document_id>/<filename>"""
    return f"{settings.ATTACHMENT_MEDIA_DIR}/{instance.document.id}/{filename}"


def get_document_attachment_directory_path(instance):
    """Get the root directory for a document's attachments.

    :type instance: documents.models.Document
    """
    return f"{settings.ATTACHMENT_MEDIA_DIR}/{instance.id}/"
