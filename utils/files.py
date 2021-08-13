import logging
import os
import shutil
from pathlib import Path
from typing import Union

from sentry_sdk import capture_exception

logger = logging.getLogger(__name__)


def remove_instance_file(instance, field_name):
    file = getattr(instance, field_name, None)
    if file:
        remove_file(file.path)


def remove_file(path: Union[Path, str]):
    try:
        os.unlink(path)
    except FileNotFoundError as e:
        logger.warning(e)
        capture_exception(e)


def remove_directory(path: Union[Path, str]):
    if os.path.exists(path):
        shutil.rmtree(path)


def b_to_mb(b: int):
    """Convert bytes to MB."""
    return round(float(b) / (1024 ** 2), 2)
