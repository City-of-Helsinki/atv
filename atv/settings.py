import os

import environ
import sentry_sdk
from corsheaders.defaults import default_headers
from django.core.exceptions import ImproperlyConfigured
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.types import SamplingContext

from utils.exceptions import sentry_before_send

checkout_dir = environ.Path(__file__) - 2
assert os.path.exists(checkout_dir("manage.py"))

parent_dir = checkout_dir.path("..")
if os.path.isdir(parent_dir("etc")):
    env_file = parent_dir("etc/env")
    default_var_root = environ.Path(parent_dir("var"))
else:
    env_file = checkout_dir(".env")
    default_var_root = environ.Path(checkout_dir("var"))

env = environ.Env(
    # Resilient logger config
    AUDIT_LOG_ENV=(str, ""),
    AUDIT_LOG_ES_URL=(str, ""),
    AUDIT_LOG_ES_INDEX=(str, ""),
    AUDIT_LOG_ES_USERNAME=(str, ""),
    AUDIT_LOG_ES_PASSWORD=(str, ""),
    DEBUG=(bool, False),
    SECRET_KEY=(str, ""),
    MEDIA_ROOT=(environ.Path(), default_var_root("media")),
    STATIC_ROOT=(environ.Path(), default_var_root("static")),
    MEDIA_URL=(str, "/media/"),
    STATIC_URL=(str, "/static/"),
    ALLOWED_HOSTS=(list, ["*"]),
    USE_X_FORWARDED_HOST=(bool, False),
    DATABASE_URL=(
        str,
        "postgres://atv:atv@localhost/atv",
    ),
    DATABASE_PASSWORD=(str, ""),
    CACHE_URL=(str, "locmemcache://"),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, "local"),
    SENTRY_PROFILE_SESSION_SAMPLE_RATE=(float, None),
    SENTRY_RELEASE=(str, None),
    SENTRY_TRACES_SAMPLE_RATE=(float, None),
    SENTRY_TRACES_IGNORE_PATHS=(list, ["/healthz", "/readiness"]),
    CORS_ALLOWED_ORIGINS=(list, []),
    CORS_ALLOW_ALL_ORIGINS=(bool, False),
    CORS_ALLOW_HEADERS=(list, []),
    DEFAULT_FROM_EMAIL=(str, "no-reply@hel.fi"),
    DJANGO_LOG_LEVEL=(str, "INFO"),
    CSRF_TRUSTED_ORIGINS=(list, []),
    API_KEY_CUSTOM_HEADER=(str, "HTTP_X_API_KEY"),
    FIELD_ENCRYPTION_KEYS=(list, []),
    ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION=(bool, True),
    ENABLE_SWAGGER_UI=(bool, True),
    USE_X_FORWARDED_FOR=(bool, True),
    TOKEN_AUTH_ACCEPTED_AUDIENCE=(list, []),
    TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=(list, []),
    TOKEN_AUTH_REQUIRE_SCOPE=(bool, False),
    TOKEN_AUTH_AUTHSERVER_URL=(list, []),
    CLAMAV_HOST=(str, "atv-clamav"),
)
if os.path.exists(env_file):
    env.read_env(env_file)

SENTRY_TRACES_SAMPLE_RATE = env("SENTRY_TRACES_SAMPLE_RATE")
SENTRY_TRACES_IGNORE_PATHS = env("SENTRY_TRACES_IGNORE_PATHS")


def sentry_traces_sampler(sampling_context: SamplingContext) -> float:
    # Respect parent sampling decision if one exists. Recommended by Sentry.
    if (parent_sampled := sampling_context.get("parent_sampled")) is not None:
        return float(parent_sampled)

    # Exclude health check endpoints from tracing
    path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO", "")
    if path.rstrip("/") in SENTRY_TRACES_IGNORE_PATHS:
        return 0

    # Use configured sample rate for all other requests
    return SENTRY_TRACES_SAMPLE_RATE or 0


if env("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        environment=env("SENTRY_ENVIRONMENT"),
        release=env("SENTRY_RELEASE"),
        integrations=[DjangoIntegration()],
        traces_sampler=sentry_traces_sampler,
        profile_session_sample_rate=env("SENTRY_PROFILE_SESSION_SAMPLE_RATE"),
        profile_lifecycle="trace",
        before_send=sentry_before_send,
    )

BASE_DIR = str(checkout_dir)

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
if DEBUG and not SECRET_KEY:
    SECRET_KEY = "xxx"

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
USE_X_FORWARDED_HOST = env("USE_X_FORWARDED_HOST")

if env("CSRF_TRUSTED_ORIGINS"):
    CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

DATABASES = {"default": env.db()}

if env("DATABASE_PASSWORD"):
    DATABASES["default"]["PASSWORD"] = env("DATABASE_PASSWORD")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CACHES = {"default": env.cache()}

MEDIA_ROOT = env("MEDIA_ROOT")
STATIC_ROOT = env("STATIC_ROOT")
MEDIA_URL = env("MEDIA_URL")
STATIC_URL = env("STATIC_URL")

FILE_UPLOAD_PERMISSIONS = None

ROOT_URLCONF = "atv.urls"
WSGI_APPLICATION = "atv.wsgi.application"

LANGUAGES = (("fi", "Finnish"), ("en", "English"), ("sv", "Swedish"))

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Helsinki"
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

INSTALLED_APPS = [
    # 3rd party
    "helusers.apps.HelusersConfig",
    "helusers.apps.HelusersAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_api_key",
    "django_filters",
    "corsheaders",
    "encrypted_fields",
    "guardian",
    "drf_spectacular",
    # Local apps
    "users",
    "services",
    "documents",
    "audit_log",
    "logger_extra",
    "resilient_logger",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "logger_extra.middleware.XRequestIdMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS")
CORS_ALLOW_HEADERS = tuple(
    list(default_headers) + ["baggage", "sentry-trace"] + env.list("CORS_ALLOW_HEADERS")
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "helusers.oidc.ApiTokenAuthentication",
        "atv.authentication.ServiceApiKeyAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "utils.api.PageNumberPagination",
    "ORDERING_PARAM": "sort",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX": "",
    "EXCEPTION_HANDLER": "utils.exceptions.custom_exception_handler",
}

ATTACHMENT_MEDIA_DIR = "attachments"
ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION = env.bool(
    "ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION"
)
MAX_FILE_SIZE = 20971520  # 20 MiB
MAX_FILE_UPLOAD_ALLOWED = 10

# Authentication

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]

API_KEY_CUSTOM_HEADER = env("API_KEY_CUSTOM_HEADER")

OIDC_API_TOKEN_AUTH = {
    "AUDIENCE": env("TOKEN_AUTH_ACCEPTED_AUDIENCE"),
    "API_SCOPE_PREFIX": env("TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX"),
    "ISSUER": env("TOKEN_AUTH_AUTHSERVER_URL"),
    "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": env("TOKEN_AUTH_REQUIRE_SCOPE"),
}

# Encryption

FIELD_ENCRYPTION_KEYS = env("FIELD_ENCRYPTION_KEYS")
DEBUG_FIELD_ENCRYPTION_KEY = (
    "cde167fade57af385584c43b1cff391e9ded59c65cf229276b5f6f55a9a73dfc"
)

if DEBUG and not FIELD_ENCRYPTION_KEYS:
    FIELD_ENCRYPTION_KEYS = [DEBUG_FIELD_ENCRYPTION_KEY]

if not DEBUG and DEBUG_FIELD_ENCRYPTION_KEY in FIELD_ENCRYPTION_KEYS:
    raise ImproperlyConfigured("Cannot use the debug encryption key in production")

# API Documentation
ENABLE_SWAGGER_UI = env("ENABLE_SWAGGER_UI")

SPECTACULAR_SETTINGS = {
    "TITLE": " Asiointitietovaranto ",
    "DESCRIPTION": "Asiointitietovaranto REST API",
    "VERSION": "0.1.0",
}

# Audit logging
# Resilient logger settings
RESILIENT_LOGGER = {
    "origin": "atv",
    "environment": env("AUDIT_LOG_ENV"),
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
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
}


USE_X_FORWARDED_FOR = env("USE_X_FORWARDED_FOR")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "context": {"()": "logger_extra.filter.LoggerContextFilter"},
    },
    "formatters": {
        "json": {"()": "logger_extra.formatter.JSONFormatter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["context"],
        }
    },
    "loggers": {"": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL")}},
}

# Malware Protection
CLAMAV_HOST = env("CLAMAV_HOST")

HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED = True
