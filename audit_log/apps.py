from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuditLogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit_log"
    verbose_name = _("audit log")
