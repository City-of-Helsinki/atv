from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from atv.exceptions import MaximumFileSizeExceededException
from documents.fields import EncryptedFileField, EncryptedJSONField
from documents.utils import get_attachment_file_path
from documents.validators import BusinessIDValidator
from services.models import Service
from utils.models import TimestampedModel, UUIDModel


class Activity(models.Model):
    status = models.ForeignKey(
        "StatusHistory", on_delete=models.CASCADE, related_name="activities"
    )
    title = models.JSONField(
        default=dict,
        verbose_name=_("title"),
        help_text=_("Title for activity/activity message"),
    )
    message = models.JSONField(
        default=dict,
        blank=True,
        help_text=_(
            "Message/description of activity for internal use, or for showing to user"
        ),
    )
    activity_links = models.JSONField(
        default=dict,
        blank=True,
        help_text=_(
            "Structure with links related to activity with display text in multiple"
            " languages"
        ),
    )
    show_to_user = models.BooleanField(
        help_text=_("Set whether the activity is shown to end user"), default=False
    )
    activity_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activity_timestamp"]


class StatusHistory(models.Model):
    document = models.ForeignKey(
        "Document", on_delete=models.CASCADE, related_name="status_histories"
    )
    value = models.CharField(max_length=255, blank=True)
    status_display_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("status_display_values"),
        help_text=_(
            "Status display values/translations."
            " It's recommended to use ISO 639-1 language codes as key values."
        ),
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class Attachment(TimestampedModel):
    document = models.ForeignKey(
        "Document",
        on_delete=models.CASCADE,
        verbose_name=_("attachment"),
        related_name="attachments",
        help_text=_("Document to which the file is attached."),
    )
    media_type = models.CharField(
        max_length=255,
        default="",
        verbose_name=_("media type"),
        help_text=_("The media type of the attachment."),
    )
    size = models.PositiveIntegerField(
        verbose_name=_("size"),
        help_text=_("Size of the attachment in bytes."),
    )
    filename = models.CharField(
        max_length=255,
        verbose_name=_("filename"),
        help_text=_("The original filename of the attachment."),
    )
    file = EncryptedFileField(
        upload_to=get_attachment_file_path,
        verbose_name=_("file"),
        help_text=_("Encrypted file."),
    )

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        default_related_name = "attachments"

    def __str__(self):
        return f"Attachment {self.pk}"

    @property
    def uri(self):
        return reverse("documents-attachments-detail", args=[self.document.id, self.id])

    def clean(self):
        if self.file.size > settings.MAX_FILE_SIZE:
            raise MaximumFileSizeExceededException()

    def save(self, *args, **kwargs):
        self.size = self.file.size
        self.filename = self.file.name

        self.full_clean()

        super().save(*args, **kwargs)


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
            "(e.g. the id from"
            " https://api.hel.fi/helerm/v1/function/eb30af1d9d654ebc98287ca25f231bf6/"
            ") which is applied to the stored document when considering storage time."
        ),
    )
    tos_record_id = models.CharField(
        max_length=32,
        verbose_name=_("TOS record ID"),
        help_text=_(
            "UUID without dashes. Should correspond to a record ID "
            "(e.g. records[].id from"
            " https://api.hel.fi/helerm/v1/function/eb30af1d9d654ebc98287ca25f231bf6/"
            ") within a Function instance which is applied to the stored document when "
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
        encoder=DjangoJSONEncoder,
        verbose_name=_("metadata"),
        help_text=_(
            "Key-value pairs given by the calling service. These fields should enable "
            "the service to store some relevant information which it can use to "
            "filter/sort documents, e.g. the handler of the document."
        ),
    )
    content = EncryptedJSONField(
        help_text=_("Encrypted content of the document."), default=dict, blank=True
    )
    status = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Status information given by the owning service. "
            "Could be e.g. some constant string."
        ),
    )
    status_display_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("status_display_values"),
        help_text=_(
            "Status display values/translations."
            " It's recommended to use ISO 639-1 language codes as key values."
        ),
    )
    status_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        default=timezone.now,
        verbose_name=_("status_timestamp"),
        help_text=_(
            "Date and time when document status was last changed. Field is"
            " automatically set."
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
    human_readable_type = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("human_readable_type"),
        help_text=_(
            "Document type and translations for end user."
            " It's recommended to use ISO 639-1 language codes as key values."
        ),
    )
    deletable = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        verbose_name=_("deletable"),
        help_text=_("Is document deletable by user."),
    )
    document_language = models.CharField(
        null=True,
        blank=True,
        help_text=_("ISO 639-1 Language code of document content if known"),
        max_length=5,
    )
    content_schema_url = models.URLField(
        null=True, blank=True, help_text=_("Link to content schema if available")
    )
    delete_after = models.DateField(
        null=True,
        help_text=_(
            "Date which after the document and related attachments are permanently"
            " deleted"
        ),
    )

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        default_related_name = "documents"
        indexes = [
            models.Index(fields=["created_at"], name="document_created_at_idx"),
            models.Index(fields=["updated_at"], name="document_updated_at_idx"),
            models.Index(fields=["business_id"], name="document_business_id_idx"),
            models.Index(fields=["transaction_id"], name="document_transaction_id_idx"),
            models.Index(fields=["draft"], name="document_draft_idx"),
            models.Index(fields=["locked_after"], name="document_locked_after_idx"),
            GinIndex(fields=["metadata"], name="document_metadata_idx"),
            models.Index(fields=["status"], name="document_status_idx"),
            models.Index(fields=["type"], name="document_type_idx"),
        ]

    def __str__(self):
        return f"Document {self.pk}"
