# Audit Logging

## Settings

* `AUDIT_LOG_ORIGIN`, string set to the audit logs origin field
* `ELASTIC_AUDIT_LOG_INDEX`, index to which the data is sent to
* `ELASTIC_HOST`
* `ELASTIC_PORT`
* `ELASTIC_SSL`, will the connection use encryption
* `ELASTIC_USERNAME`
* `ELASTIC_PASSWORD`
* `ELASTIC_CREATE_DATA_STREAM`, will try to create a data stream
* `ENABLE_SEND_AUDIT_LOG`, will the audit logs be sent to ElasticSearch


## Usage

An audit logging package that can be used with `djangorestframework`.

This audit logger allows you to save log messages from Django Rest Framework
CRUD events to database. The serializer works by defining a DRF model viewset
that inherits `AuditLoggingModelViewSet`.

To start using this package, follow these steps:

1. Add `djangorestframework` to requirements and add this setting:
    ```python
    env = environ.Env(
        ...,
        AUDIT_LOG_ORIGIN=(str, ""),
    )

    # Audit logging
    AUDIT_LOG_ORIGIN = env.str("AUDIT_LOG_ORIGIN")

    INSTALLED_APPS = [
        ...,
        "audit_log",
    ]
    ```

2. Add `AUDIT_LOG_ORIGIN` to env variables.

3. Create a DRF viewset that inherits `audit_log.viewsets.AuditLoggingModelViewSet`.
   It will log all the CRUD events of that viewset.

Manual logging can also be done using the log function
`audit_log.audit_logging.log`:

```python
from django.contrib.auth import get_user_model

from documents.models import Document
from audit_log import audit_logging
from audit_log.enums import Operation

User = get_user_model()

document = Document.objects.last()
user = User.objects.last()

do_something(document)

audit_logging.log(
    user,
    "",  # Optional user backend
    Operation.UPDATE,
    document,
    additional_information="document was processed!",
)
```

Based on:
- [apartment-application-service audit logging](https://github.com/City-of-Helsinki/apartment-application-service/tree/develop/audit_log)
- [Helsinki Profile logging format](https://helsinkisolutionoffice.atlassian.net/wiki/spaces/KAN/pages/416972828/Helsinki+profile+audit+logging#Profile-audit-log---CRUD-events---JSON-content-and-format)
- [YJDH Audit logging implemetation](https://github.com/City-of-Helsinki/yjdh/tree/main/backend/shared/shared/audit_log)
- [YJDH Audit logging specification](https://helsinkisolutionoffice.atlassian.net/wiki/spaces/KAN/pages/7494172830/Audit+logging+specification)
