import shutil

import pytest  # noqa
from pytest_factoryboy import register

from atv.tests.conftest import *  # noqa
from services.tests.conftest import *  # noqa
from users.tests.conftest import *  # noqa

from ..models import Activity, StatusHistory
from .factories import AttachmentFactory, DocumentFactory


@pytest.fixture(autouse=True)
def custom_media_dir_for_files(settings, request):
    settings.MEDIA_ROOT = "test_media"

    # Teardown to remove the uploaded test files from the system
    def remove_uploaded_files():
        shutil.rmtree("test_media", ignore_errors=True)

    request.addfinalizer(remove_uploaded_files)


@pytest.fixture
def documents_with_nested_activities(service):
    """Creates 3 documents with 2 status histories each, 2 activities per history."""
    for i in range(3):
        doc = DocumentFactory(service=service)
        for j in range(2):
            status_history = StatusHistory.objects.create(
                document=doc, value=f"status_{i}_{j}"
            )
            for k in range(2):
                Activity.objects.create(
                    status=status_history,
                    title={"en": f"Activity {i}_{j}_{k}"},
                    show_to_user=True,
                )


register(DocumentFactory)
register(AttachmentFactory)
