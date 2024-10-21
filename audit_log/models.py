from typing import Optional

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AuditLogEntry(models.Model):
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    message = models.JSONField(verbose_name=_("message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        verbose_name_plural = "audit log entries"

    def __str__(self):
        return ' '.join(
            [
                _safe_get(self.message, "audit_event", "date_time"),
                _safe_get(self.message, "audit_event", "actor", "role"),
                _safe_get(self.message, "audit_event", "actor", "user_id"),
                _safe_get(self.message, "audit_event", "operation"),
                _safe_get(self.message, "audit_event", "target", "type").upper(),
                _safe_get(self.message, "audit_event", "target", "id"),
                "(SENT)" if self.is_sent else "(NOT SENT)",
            ]
        )

    @property
    def timestamp(self):
        return (
            _safe_get(self.message, "audit_event", "date_time", empty_none=True)
            or timezone.now()
        )


def _safe_get(value: dict, *keys: str, empty_none=False) -> Optional[str]:
    """Look up a nested key in the given dict, or return "UNKNOWN" on KeyError."""
    for key in keys:
        try:
            value = value[key]
        except KeyError:
            return "UNKNOWN" if not empty_none else None
    return str(value)
