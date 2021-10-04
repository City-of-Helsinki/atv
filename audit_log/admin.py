from django.contrib import admin

from audit_log.models import AuditLogEntry


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    fields = ("id", "created_at", "message")
    list_display = ("__str__", "created_at")
    list_filter = ("created_at", "is_sent")
    readonly_fields = ("id", "created_at", "message")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
