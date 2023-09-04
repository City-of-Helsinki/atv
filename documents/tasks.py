import logging

from django.utils import timezone

from documents.models import Document

logger = logging.getLogger(__name__)


def delete_expired_documents():
    """Delete expired documents and all related objects and files"""
    documents_to_delete_qs = Document.objects.filter(delete_after__lt=timezone.now())

    total, by_type_dict = documents_to_delete_qs.delete()
    if total != 0:
        logger.info(
            f"Deleted {total} objects: {', '.join([f'{i[1]} {i[0]}' for i in by_type_dict.items()])}."
        )
    else:
        logger.info("Nothing to delete.")
