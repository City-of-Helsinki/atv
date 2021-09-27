# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_create_attachment 1"] = {
    "created_at": "2021-06-30T12:00:00+03:00",
    "filename": "document1.pdf",
    "href": "http://testserver/v1/documents/5209bdd0-e626-4a7d-aa4d-73aaf961a93f/attachments/1/",
    "media_type": "application/pdf",
    "size": 12,
    "updated_at": "2021-06-30T12:00:00+03:00",
}
