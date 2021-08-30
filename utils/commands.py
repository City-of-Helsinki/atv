import logging

from django.core.management import BaseCommand as DjangoBaseCommand


class BaseCommand(DjangoBaseCommand):
    logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Dry run, don't delete any of the files or directories",
        )

    def setup_logging(self, verbosity):
        """
        The values passed by the command are:
        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output

        So output of 2 or 3 (i.e. > 1) will be verbose
        Defaults to 1
        """
        if verbosity > 1:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
