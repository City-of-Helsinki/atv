from audit_log.models import AuditLogEntry


def test_audit_log_string_representation_with_all_fields_present(settings):
    time = "2020-06-01T00:00:00.000Z"
    identifier = "f1e33c3b-2137-4bf1-926f-0a2ca013f0b5"
    log = AuditLogEntry(
        message={
            "audit_event": {
                "origin": settings.AUDIT_LOG_ORIGIN,
                "status": "SUCCESS",
                "date_time_epoch": 1590969600000,
                "date_time": time,
                "actor": {"role": "OWNER", "user_id": identifier},
                "operation": "READ",
                "target": {"id": identifier, "type": "ModelX"},
            }
        }
    )
    assert str(log) == f"{time} OWNER {identifier} READ MODELX {identifier} (NOT SENT)"


def test_audit_log_string_representation_missing_field_is_replaced_with_unknown(
    settings,
):
    time = "2020-06-01T00:00:00.000Z"
    identifier = "e69600ec-1a2d-4839-b4b8-8c807dd7e5d4"
    log = AuditLogEntry(
        message={
            "audit_event": {
                "origin": settings.AUDIT_LOG_ORIGIN,
                "status": "SUCCESS",
                "date_time_epoch": 1590969600000,
                "date_time": time,
                "actor": {"role": "USER", "user_id": identifier},
                "operation": "WRITE",
                "target": {"id": identifier},
            }
        }
    )
    assert str(log) == f"{time} USER {identifier} WRITE UNKNOWN {identifier} (NOT SENT)"
