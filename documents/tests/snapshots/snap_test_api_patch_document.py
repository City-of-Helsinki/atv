# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_update_document_owner 1"] = {
    "business_id": "1234567-8",
    "content": {
        "formData": {
            "birthDate": "3.11.1957",
            "firstName": "Dolph",
            "lastName": "Lundgren",
        },
        "reasonForApplication": "No reason, just testing",
    },
    "content_schema_url": None,
    "created_at": "2021-06-30T12:00:00+03:00",
    "deletable": True,
    "delete_after": None,
    "document_language": None,
    "draft": False,
    "id": "2d2b7a36-a306-4e35-990f-13aea04263ff",
    "locked_after": None,
    "metadata": {"created_by": "alex", "testing": True},
    "service": "service 155",
    "status": {
        "timestamp": "2021-06-30T12:00:00+03:00",
        "value": "handled",
        "status_display_values": {},
    },
    "status_histories": [],
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "type": "mysterious form",
    "human_readable_type": {},
    "updated_at": "2021-06-30T12:00:00+03:00",
}

snapshots["test_update_document_staff 1"] = {
    "business_id": "1234567-8",
    "content": {
        "formData": {
            "birthDate": "3.11.1957",
            "firstName": "Dolph",
            "lastName": "Lundgren",
        },
        "reasonForApplication": "No reason, just testing",
    },
    "content_schema_url": "https://schema.fi",
    "created_at": "2021-06-30T12:00:00+03:00",
    "deletable": False,
    "delete_after": None,
    "document_language": "en",
    "draft": True,
    "id": "2d2b7a36-a306-4e35-990f-13aea04263ff",
    "locked_after": None,
    "metadata": {"created_by": "alex", "testing": True},
    "service": "service 161",
    "status": {
        "timestamp": "2021-06-30T12:00:00+03:00",
        "value": "handled",
        "status_display_values": {"fi": "Käsitelty"},
    },
    "status_histories": [],
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "type": "mysterious form",
    "human_readable_type": {"en": "Mysterious Form"},
    "updated_at": "2021-06-30T12:00:00+03:00",
}

snapshots["test_update_document_staff_non_draft 1"] = {
    "attachments": [],
    "business_id": "1234567-8",
    "content": {
        "formData": {
            "birthDate": "3.11.1957",
            "firstName": "Dolph",
            "lastName": "Lundgren",
        },
        "reasonForApplication": "No reason, just testing",
    },
    "content_schema_url": "https://schema.fi",
    "created_at": "2021-06-30T12:00:00+03:00",
    "deletable": False,
    "delete_after": None,
    "document_language": "en",
    "draft": False,
    "id": "2d2b7a36-a306-4e35-990f-13aea04263ff",
    "locked_after": None,
    "metadata": {"created_by": "alex", "testing": True},
    "service": "service 163",
    "status": {
        "timestamp": "2021-06-30T12:00:00+03:00",
        "value": "handled",
        "status_display_values": {"fi": "Käsitelty"},
    },
    "status_histories": [],
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "type": "mysterious form",
    "human_readable_type": {"en": "Mysterious Form"},
    "updated_at": "2021-06-30T12:00:00+03:00",
}
