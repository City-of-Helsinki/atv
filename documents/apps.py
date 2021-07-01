from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "documents"
    verbose_name = _("documents")

    def ready(self):
        import documents.signals  # noqa
