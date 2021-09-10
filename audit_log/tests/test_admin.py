from django.contrib.admin import AdminSite

from audit_log.admin import AuditLogEntryAdmin
from audit_log.models import AuditLogEntry


def test_audit_log_admin_shown_fields(rf, superuser):
    request = rf.get("/")
    request.user = superuser
    model_admin = AuditLogEntryAdmin(AuditLogEntry, AdminSite())
    assert list(model_admin.get_fields(request)) == ["id", "created_at", "message"]


def test_audit_log_admin_permissions(rf, superuser):
    request = rf.get("/")
    request.user = superuser
    audit_log = AuditLogEntry.objects.create(message={})
    model_admin = AuditLogEntryAdmin(AuditLogEntry, AdminSite())
    # The user should have permission to view but not modify or delete audit logs
    assert model_admin.has_view_permission(request, audit_log)
    assert not model_admin.has_add_permission(request)
    assert not model_admin.has_change_permission(request, audit_log)
    assert not model_admin.has_delete_permission(request, audit_log)
