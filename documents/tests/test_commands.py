from datetime import timezone
from pathlib import Path
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.core.management import call_command

from documents.models import Activity, Attachment, Document, StatusHistory
from documents.tests.factories import AttachmentFactory, DocumentFactory


def test_call_remove_outdated_files():
    call_command("remove_outdated_files")


def test_call_remove_extra_files(settings, document):
    """Create an extra attachment file for a document and make sure it will get removed."""
    attachment_path = Path(
        f"{settings.MEDIA_ROOT}/{settings.ATTACHMENT_MEDIA_DIR}/{document.pk}"
    )
    attachment_path.mkdir(parents=True, exist_ok=True)

    file_to_remove = attachment_path.joinpath("remove_me.file")
    file_to_remove.touch()

    assert file_to_remove.exists()
    call_command("remove_outdated_files")
    assert not file_to_remove.exists()


def test_call_remove_extra_directories(settings):
    """Create an extra directory for a document and make sure it will get removed."""
    path_to_remove = Path(
        f"{settings.MEDIA_ROOT}/{settings.ATTACHMENT_MEDIA_DIR}/{uuid4()}"
    )
    path_to_remove.mkdir(parents=True, exist_ok=True)
    assert path_to_remove.exists()
    call_command("remove_outdated_files")
    assert not path_to_remove.exists()


def test_delete_expired_documents(service):
    document1 = DocumentFactory(
        service=service, delete_after=today(timezone.utc) - relativedelta(days=1)
    )
    document2 = DocumentFactory(
        service=service, delete_after=today(timezone.utc) + relativedelta(days=2)
    )

    AttachmentFactory(document=document1)
    AttachmentFactory(document=document2)

    status_history1 = StatusHistory.objects.create(document=document1)
    status_history2 = StatusHistory.objects.create(document=document2)

    Activity.objects.create(status=status_history1)
    Activity.objects.create(status=status_history2)

    assert Document.objects.count() == 2
    assert Attachment.objects.count() == 2
    assert Activity.objects.count() == 2
    call_command("delete_expired_documents")

    assert Document.objects.count() == 1
    assert Attachment.objects.count() == 1
    assert StatusHistory.objects.count() == 1
