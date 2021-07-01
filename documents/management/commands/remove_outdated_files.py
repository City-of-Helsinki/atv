import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from documents.models import Document
from documents.utils import get_document_directory_path
from utils.files import remove_directory, remove_file

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Add admin user"

    directories_to_delete = 0
    files_to_delete = 0

    directories_deleted = 0
    files_deleted = 0

    @staticmethod
    def setup_logging(verbosity):
        """
        The values passed by the command are:
        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output

        So output of 2 or 3 (i.e. > 1) will be verbose
        Defaults to 1
        """
        if verbosity > 1:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Dry run, don't delete any of the files or directories",
        )

    def remove_document_outdated_files(self, document: Document, path, dry_run):
        """For a given document, remove the files that don't have an associated Attachment"""
        document_path = get_document_directory_path(document)

        for filename in os.listdir(path):
            # For each file on the Document directory, check if the instance
            # still has the related Attachment.
            # If there's no attachment, the file will be removed
            if not document.attachments.filter(
                file=os.path.join(document_path, filename)
            ).exists():
                if dry_run:
                    self.files_to_delete += 1
                else:
                    file_path = os.path.join(path, filename)
                    remove_file(file_path)
                    self.files_deleted += 1
                    logger.debug(f"File removed: {file_path}")

    def remove_outdated_document_directories(self, root_dir, dry_run):
        for document_id in os.listdir(root_dir):
            document_path = os.path.join(root_dir, document_id)

            if document := Document.objects.filter(id=document_id).first():
                logger.debug(f"Document {document_id} exists")
                self.remove_document_outdated_files(document, document_path, dry_run)
            elif dry_run:
                self.directories_to_delete += 1
            else:
                # If the document does not exist anymore, remove the whole directory
                remove_directory(document_path)
                self.directories_deleted += 1
                logger.debug(f"Directory removed: {document_path}")

    def handle(self, dry_run: bool = False, verbosity: int = 0, *args, **kwargs):
        self.setup_logging(verbosity)

        root_dir = settings.ATTACHMENT_VOLUME_PATH

        self.remove_outdated_document_directories(root_dir, dry_run)

        if dry_run:
            logger.info(f"Directories to be removed: {self.directories_to_delete}")
            logger.info(f"Files to be removed: {self.files_to_delete}")
        else:
            logger.info(f"Directories removed: {self.directories_deleted}")
            logger.info(f"Files removed: {self.files_deleted}")
