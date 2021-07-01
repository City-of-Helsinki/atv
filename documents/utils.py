def get_attachment_file_path(instance, filename):
    """File will be uploaded to MEDIA_ROOT/<document_id>/<filename>"""
    return f"{instance.document.id}/{filename}"


def get_attachment_directory_path(instance):
    """Get the root directory for an attachment"""
    return f"{instance.document.id}/"


def get_document_directory_path(instance):
    """Get the root directory for a document"""
    return f"{instance.id}/"
