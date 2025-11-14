import logging
from datetime import datetime, timezone
from typing import Optional, Union

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.db.models.base import ModelBase
from resilient_logger.sources import ResilientLogSource

from audit_log.enums import Operation, Role, Status

User = get_user_model()


def _now() -> datetime:
    """Returns the current time in UTC timezone."""
    return datetime.now(tz=timezone.utc)


def log(
    actor: Optional[Union[User, AnonymousUser]],
    actor_backend: str,
    operation: Operation,
    target: Union[Model, ModelBase],
    status: Status = Status.SUCCESS,
    ip_address: str = "",
    additional_information: str = "",
    service=None,
    view_name: str = "",
    lookup_field: str = "",
):
    """
    Write an event to the audit log.

    Each audit log event has an actor (or None for system events),
    an operation(e.g. READ or UPDATE), the target of the operation
    (a Django model instance), status (e.g. SUCCESS), and a timestamp.
    """
    user_id_field_name = getattr(actor, "audit_log_id_field", "pk")
    user_id = str(getattr(actor, user_id_field_name, None) or "")

    if actor is None:
        role = Role.SYSTEM
    elif actor.is_superuser:
        role = Role.ADMIN
    elif isinstance(actor, AnonymousUser):
        role = Role.ANONYMOUS
    elif actor.id == target.pk:
        role = Role.OWNER
    else:
        role = Role.USER

    actor_data = {
        "role": role.value,
        "user_id": user_id,
        "provider": actor_backend if actor_backend else "",
        "ip_address": ip_address,
    }
    if service:
        actor_data["service"] = service.name
        actor_data["authentication"] = (
            "API-Key" if hasattr(actor, "service_api_key") else "Token"
        )
    target_id = _get_target_id(target)

    ResilientLogSource.create_structured(
        level=logging.NOTSET,
        message=status.value,
        actor=actor_data,
        operation=operation.value,
        target={
            "type": _get_target_type(target),
            "id": target_id,
            "lookup_field": lookup_field if target_id else "",
            "endpoint": view_name,
        },
        extra={"status": status, "additional_information": additional_information},
    )


def _get_target_id(target: Union[Model, ModelBase]) -> str:
    if isinstance(target, ModelBase):
        return ""
    field_name = getattr(target, "audit_log_id_field", "pk")
    audit_log_id = getattr(target, field_name, "")
    return str(audit_log_id)


def _get_target_type(target: Union[Model, ModelBase]) -> str:
    return (
        str(target.__class__.__name__)
        if isinstance(target, Model)
        else str(target.__name__)
    )
