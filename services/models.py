from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_api_key.models import AbstractAPIKey

from services.enums import ServicePermissions
from utils.models import TimestampedModel


class Service(TimestampedModel):
    name = models.CharField(verbose_name=_("name"), max_length=50)
    description = models.TextField(verbose_name=_("description"), blank=True)

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")
        permissions = ServicePermissions.choices

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


class ServiceClientId(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="client_ids",
        verbose_name=_("service"),
    )
    client_id = models.CharField(
        max_length=256,
        unique=True,
        verbose_name=_("client ID"),
        help_text=_("Client ID of the OIDC token which identifies the used service."),
    )

    class Meta:
        verbose_name = _("client ID")
        verbose_name_plural = _("client IDs")

    def __str__(self) -> str:
        return f"{self.service.name}: {self.client_id}"
