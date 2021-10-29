# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_create_anonymous_document 1"] = {
    "business_id": "1234567-8",
    "content": {
        "formData": {
            "birthDate": "3.11.1957",
            "firstName": "Dolph",
            "lastName": "Lundgren",
        },
        "reasonForApplication": "No reason, just testing",
    },
    "created_at": "2021-06-30T12:00:00+03:00",
    "draft": False,
    "locked_after": None,
    "metadata": {"created_by": "alex", "testing": True},
    "status": "handled",
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "type": "mysterious form",
    "updated_at": "2021-06-30T12:00:00+03:00",
    "user_id": None,
}

snapshots["test_create_authenticated_document 1"] = {
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
    "created_at": "2021-06-30T12:00:00+03:00",
    "draft": False,
    "locked_after": None,
    "metadata": {"created_by": "alex", "testing": True},
    "status": "handled",
    "tos_function_id": "f917d43aab76420bb2ec53f6684da7f7",
    "tos_record_id": "89837a682b5d410e861f8f3688154163",
    "transaction_id": "cf0a341b-6bfd-4f59-8d7c-87bf62ba837b",
    "type": "mysterious form",
    "updated_at": "2021-06-30T12:00:00+03:00",
}
