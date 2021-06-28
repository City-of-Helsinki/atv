from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_api_key.models import AbstractAPIKey

from utils.models import TimestampedModel


class Service(TimestampedModel):
    name = models.CharField(verbose_name=_("name"), max_length=50)
    description = models.TextField(verbose_name=_("description"), blank=True)

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self) -> str:
        return self.name


class ServiceAPIKey(AbstractAPIKey):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = _("service API key")
        verbose_name_plural = _("service API keys")
