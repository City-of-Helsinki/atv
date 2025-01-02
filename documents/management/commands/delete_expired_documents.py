from django.core.management.base import BaseCommand

from documents.tasks import delete_expired_documents


class Command(BaseCommand):
    help = (
        "Delete documents and related objects and files that have reached their"
        " deletion date"
    )

    def handle(self, *args, **kwargs):
        delete_expired_documents()
