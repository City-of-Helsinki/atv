from datetime import datetime, timezone
from typing import Callable, Optional, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.db.models.base import ModelBase

from audit_log.enums import Operation, Role, Status
from audit_log.models import AuditLogEntry

User = get_user_model()


def _now() -> datetime:
    """Returns the current time in UTC timezone."""
    return datetime.now(tz=timezone.utc)


def _iso8601_date(time: datetime) -> str:
    """Formats the timestamp in ISO-8601 format, e.g. '2020-06-01T00:00:00.000Z'."""
    return f"{time.replace(tzinfo=None).isoformat(timespec='milliseconds')}Z"


def log(
    actor: Optional[Union[User, AnonymousUser]],
    actor_backend: str,
    operation: Operation,
    target: Union[Model, ModelBase],
    status: Status = Status.SUCCESS,
    get_time: Callable[[], datetime] = _now,
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
    current_time = get_time()
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
    message = {
        "audit_event": {
            "origin": settings.AUDIT_LOG_ORIGIN,
            "status": status.value,
            "date_time_epoch": int(current_time.timestamp() * 1000),
            "date_time": _iso8601_date(current_time),
            "actor": actor_data,
            "operation": operation.value,
            "additional_information": additional_information,
            "target": {
                "type": _get_target_type(target),
                "id": target_id,
                "lookup_field": lookup_field if target_id else "",
                "endpoint": view_name,
            },
        },
    }
    AuditLogEntry.objects.create(message=message)


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
