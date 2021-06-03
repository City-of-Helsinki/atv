from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


@admin.register(get_user_model())
class UserAdmin(DjangoUserAdmin):
    list_display = DjangoUserAdmin.list_display + ("uuid",)
    fieldsets = DjangoUserAdmin.fieldsets + (("UUID", {"fields": ("uuid",)}),)
    search_fields = DjangoUserAdmin.search_fields + ("uuid",)
    readonly_fields = ("uuid",)
