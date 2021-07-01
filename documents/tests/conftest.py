import shutil
import tempfile

import pytest  # noqa

from atv.tests.conftest import *  # noqa
from services.tests.conftest import *  # noqa
from users.tests.conftest import *  # noqa


@pytest.fixture(autouse=True)
def custom_media_dir_for_files(settings, request):
    settings.ATTACHMENT_VOLUME_PATH = tempfile.mkdtemp()

    # Teardown to remove the uploaded test files from the system
    def remove_uploaded_files():
        shutil.rmtree(settings.ATTACHMENT_VOLUME_PATH, ignore_errors=False)

    request.addfinalizer(remove_uploaded_files)
