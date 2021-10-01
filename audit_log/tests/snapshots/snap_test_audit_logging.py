# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_log_actor_uuid 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "USER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "be584b90-b256-46f5-83e1-4e6a0f8b4cc3", "type": "User"},
    }
}

snapshots["test_log_anonymous_role[CREATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "ANONYMOUS",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "CREATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_anonymous_role[DELETE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "ANONYMOUS",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "DELETE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_anonymous_role[READ] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "ANONYMOUS",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_anonymous_role[UPDATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "ANONYMOUS",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "UPDATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_owner_operation[CREATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "OWNER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "CREATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_owner_operation[DELETE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "OWNER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "DELETE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_owner_operation[READ] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "OWNER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_owner_operation[UPDATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "OWNER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "UPDATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_status[FORBIDDEN] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "OWNER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "FORBIDDEN",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_status[SUCCESS] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "OWNER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_system_operation[CREATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "SYSTEM",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "CREATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_system_operation[DELETE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "SYSTEM",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "DELETE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_system_operation[READ] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "SYSTEM",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_system_operation[UPDATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "SYSTEM",
            "user_id": "",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "UPDATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}

snapshots["test_log_user_operation[CREATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "USER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "CREATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "be584b90-b256-46f5-83e1-4e6a0f8b4cc3", "type": "User"},
    }
}

snapshots["test_log_user_operation[DELETE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "USER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "DELETE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "be584b90-b256-46f5-83e1-4e6a0f8b4cc3", "type": "User"},
    }
}

snapshots["test_log_user_operation[READ] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "USER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "be584b90-b256-46f5-83e1-4e6a0f8b4cc3", "type": "User"},
    }
}

snapshots["test_log_user_operation[UPDATE] 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "",
            "role": "USER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "UPDATE",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "be584b90-b256-46f5-83e1-4e6a0f8b4cc3", "type": "User"},
    }
}

snapshots["test_log_user_with_backend 1"] = {
    "audit_event": {
        "actor": {
            "ip_address": "192.168.1.1",
            "provider": "some.auth.Backend",
            "role": "OWNER",
            "user_id": "7e564b45-527f-4ea6-92c7-3d39ba05733c",
        },
        "additional_information": "",
        "date_time": "2020-06-01T00:00:00.000Z",
        "date_time_epoch": 1590969600000,
        "operation": "READ",
        "origin": "atv",
        "status": "SUCCESS",
        "target": {"id": "7e564b45-527f-4ea6-92c7-3d39ba05733c", "type": "User"},
    }
}
