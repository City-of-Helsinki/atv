import shutil

import pytest  # noqa
from pytest_factoryboy import register

from atv.tests.conftest import *  # noqa
from services.tests.conftest import *  # noqa
from users.tests.conftest import *  # noqa

from .factories import AttachmentFactory, DocumentFactory


@pytest.fixture(autouse=True)
def custom_media_dir_for_files(settings, request):
    settings.MEDIA_ROOT = "test_media"

    # Teardown to remove the uploaded test files from the system
    def remove_uploaded_files():
        shutil.rmtree("test_media", ignore_errors=True)

    request.addfinalizer(remove_uploaded_files)


register(DocumentFactory)
register(AttachmentFactory)
