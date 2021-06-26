from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from documents.models import Document


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
