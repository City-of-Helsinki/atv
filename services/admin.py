from django.contrib import admin
from django.db.models import Count
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from guardian.admin import GuardedModelAdmin
from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey

from .models import Service, ServiceAPIKey


@admin.register(Service)
class ServiceAdmin(GuardedModelAdmin):
    list_display = ("name", "short_description", "api_key_count")
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(api_keys_count=Count("api_keys"))

    @admin.display(description=_("description"))
    def short_description(self, obj: Service):
        return truncatechars(obj.description, 255)

    @admin.display(description=_("api keys"), ordering="api_keys_count")
    def api_key_count(self, obj):
        return obj.api_keys_count


@admin.register(ServiceAPIKey)
class ServiceAPIKeyModelAdmin(APIKeyModelAdmin):
    list_display = (*APIKeyModelAdmin.list_display, "get_service_name")
    search_fields = (*APIKeyModelAdmin.search_fields, "service__name")
    autocomplete_fields = ("service",)
    list_select_related = ("service",)

    @admin.display(description=_("service"), ordering="-service__name")
    def get_service_name(self, obj):
        return obj.service.name


admin.site.unregister(APIKey)
