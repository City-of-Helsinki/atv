from django.contrib import admin
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "short_description")
    search_fields = ("name",)

    @admin.display(description=_("description"))
    def short_description(self, obj: Service):
        return truncatechars(obj.description, 255)
