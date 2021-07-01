from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from documents.models import Attachment, Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("pk", "get_service_name", "draft", "created_at", "updated_at")
    search_fields = ("service__name", "type", "status", "business_id")
    list_filter = ("draft",)
    autocomplete_fields = ("service", "user")
    list_select_related = ("service",)

    @admin.display(description=_("service"), ordering="-service__name")
    def get_service_name(self, obj):
        return obj.service.name


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "filename",
        "media_type",
        "get_size_in_mb",
        "get_document",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "filename",
        "document__id",
    )
    list_filter = ("media_type",)
    autocomplete_fields = ("document",)
    readonly_fields = (
        "filename",
        "media_type",
        "size",
    )

    @admin.display(description=_("size (MB)"))
    def get_size_in_mb(self, obj):
        if not obj.size:
            return "-"
        size_mb = round(float(obj.size) / (1024 ** 2), 2)
        return f"{size_mb}MB"

    @admin.display(description=_("Document"))
    def get_document(self, obj):
        link = reverse("admin:documents_document_change", args=[obj.document.id])
        return format_html('<a href="{}">{}</a>', link, str(obj.document))
