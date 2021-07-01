import os

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from utils.files import remove_directory, remove_instance_file

from .models import Attachment, Document
from .utils import get_document_attachment_directory_path


@receiver(
    post_delete,
    sender=Attachment,
    dispatch_uid="post_delete_attachment_file",
)
def delete_attachment_file_handler(sender, instance, **kwargs):
    """When an Attachment instance is deleted, delete also the associated stored file

    It can be enabled/disabled by switching the environment variable
    ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION={0,1} (defaults to True)
    """
    if settings.ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION:
        remove_instance_file(instance, "file")


@receiver(
    post_delete,
    sender=Document,
    dispatch_uid="post_delete_document_attachment_files",
)
def delete_document_attachment_files_handler(sender, instance, **kwargs):
    """When a document is deleted, the directory where the associated attached files
    are stored is removed

    It can be enabled/disabled by switching the environment variable
    ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION={0,1} (defaults to True)
    """
    if settings.ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION:
        path = os.path.join(
            settings.MEDIA_ROOT, get_document_attachment_directory_path(instance)
        )
        remove_directory(path)
