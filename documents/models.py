from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from documents.validators import BusinessIDValidator
from services.models import Service
from utils.models import TimestampedModel, UUIDModel


class Document(UUIDModel, TimestampedModel):
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name=_("service"),
        help_text=_("The service which owns this document."),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("user"),
        help_text=_("The creator/owner of this document."),
    )
    business_id = models.CharField(
        max_length=9,
        blank=True,
        validators=[BusinessIDValidator()],
        verbose_name=_("business ID"),
        help_text=_("The business ID of the organization which owns this document."),
    )
    # TODO Unique per service?
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("transaction ID"),
        help_text=_(
            "Transaction identifier given by the owning service. Could be e.g. a UUID."
        ),
    )
    tos_function_id = models.CharField(
        max_length=32,
        verbose_name=_("TOS function ID"),
        help_text=_(
            "UUID without dashes. Should correspond with a Function instance "
            "(e.g. the id from https://api.hel.fi/helerm/v1/function/eb30af1d9d654ebc98287ca25f231bf6/) "
            "which is applied to the stored document when considering storage time."
        ),
    )
    tos_record_id = models.CharField(
        max_length=32,
        verbose_name=_("TOS record ID"),
        help_text=_(
            "UUID without dashes. Should correspond to a record ID "
            "(e.g. records[].id from https://api.hel.fi/helerm/v1/function/eb30af1d9d654ebc98287ca25f231bf6/) "
            "within a Function instance which is applied to the stored document when "
            "considering storage time."
        ),
    )
    draft = models.BooleanField(
        default=False,
        verbose_name=_("draft"),
        help_text=_(
            "Is this document a draft or not. Drafts can be modified by a user."
        ),
    )
    locked_after = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("locked after"),
        help_text=_(
            "Date and time after which this document cannot be modified, except for "
            "deleting. This field should be filled by the calling service if it knows "
            "e.g. that a certain application has a deadline."
        ),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        # null=True,  # TODO should we allow null?
        encoder=DjangoJSONEncoder,
        verbose_name=_("metadata"),
        help_text=_(
            "Key-value pairs given by the calling service. These fields should enable "
            "the service to store some relevant information which it can use to "
            "filter/sort documents, e.g. the handler of the document."
        ),
    )
    # TODO The actual JSON content of the stored document.
    #  The format should be relevant only to the calling service.
    #  The content is encrypted before storing into the database.
    #  - content
    status = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Status information given by the owning service. "
            "Could be e.g. some constant string."
        ),
    )
    type = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("type"),
        help_text=_(
            "Type information given by the owning service. "
            "Could be e.g. the type of the document."
        ),
    )

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        default_related_name = "documents"

    def __str__(self):
        return f"Document {self.pk}"
