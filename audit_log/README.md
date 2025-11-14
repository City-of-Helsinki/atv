# Audit Logging

## Settings

This module uses [django-resilient-logger](https://github.com/City-of-Helsinki/django-resilient-logger) for audit logging. Configure the following environment variables:

* `AUDIT_LOG_ENVIRONMENT` - Environment identifier (e.g., "production", "staging")
* `AUDIT_LOG_ES_URL` - Elasticsearch URL for log storage
* `AUDIT_LOG_ES_INDEX` - Elasticsearch index name
* `AUDIT_LOG_ES_USERNAME` - Elasticsearch username
* `AUDIT_LOG_ES_PASSWORD` - Elasticsearch password

The `RESILIENT_LOGGER` configuration in `settings.py` uses these environment variables to configure the resilient logger with Elasticsearch as the target.

## Usage

An audit logging package that can be used with `djangorestframework`.

This audit logger saves log messages from Django Rest Framework CRUD events using the [`resilient_logger`](https://github.com/City-of-Helsinki/django-resilient-logger). Logs are stored in the `ResilientLogEntry` model and sent to Elasticsearch via a cronjob that calls `submit_unsent_entries`. The viewset works by defining a DRF model viewset that inherits `AuditLoggingModelViewSet`.

To start using this package, follow these steps:

1. Add `djangorestframework` and `django-resilient-logger` to requirements and configure settings:
    ```python
    env = environ.Env(
        AUDIT_LOG_ENVIRONMENT=(str, ""),
        AUDIT_LOG_ES_URL=(str, ""),
        AUDIT_LOG_ES_INDEX=(str, ""),
        AUDIT_LOG_ES_USERNAME=(str, ""),
        AUDIT_LOG_ES_PASSWORD=(str, ""),
    )

    INSTALLED_APPS = [
        ...,
        "audit_log",
        "resilient_logger",
    ]

    # Resilient logger configuration for audit logging
    RESILIENT_LOGGER = {
        "origin": "atv",
        "environment": env("AUDIT_LOG_ENVIRONMENT"),
        "sources": [
            {
                "class": "resilient_logger.sources.ResilientLogSource",
            }
        ],
        "targets": [
            {
                "class": "resilient_logger.targets.ElasticsearchLogTarget",
                "es_url": env("AUDIT_LOG_ES_URL"),
                "es_username": env("AUDIT_LOG_ES_USERNAME"),
                "es_password": env("AUDIT_LOG_ES_PASSWORD"),
                "es_index": env("AUDIT_LOG_ES_INDEX"),
                "required": True,
            }
        ],
    }
    ```

2. Set the required environment variables (`AUDIT_LOG_ENVIRONMENT`, `AUDIT_LOG_ES_URL`, etc.).

3. Create a DRF viewset that inherits `audit_log.viewsets.AuditLoggingModelViewSet`.
   It will automatically log all CRUD events of that viewset.

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

## Technical Details

This implementation uses [django-resilient-logger](https://github.com/City-of-Helsinki/django-resilient-logger) which provides:
- Reliable log delivery to Elasticsearch with retry mechanisms
- Local database storage (`ResilientLogEntry` model) before transmission
- Batch processing and submission of log entries via management command
- Graceful handling of Elasticsearch connection failures

Logs are sent to Elasticsearch by scheduling a cronjob that periodically runs `python manage.py submit_unsent_entries` to send accumulated log entries.
