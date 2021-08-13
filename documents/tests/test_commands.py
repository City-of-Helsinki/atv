from pathlib import Path
from uuid import uuid4

from django.core.management import call_command


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
