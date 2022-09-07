import os
import subprocess

import environ
import sentry_sdk
from django.core.exceptions import ImproperlyConfigured
from sentry_sdk.integrations.django import DjangoIntegration

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
    CACHE_URL=(str, "locmemcache://"),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, "development"),
    CORS_ORIGIN_WHITELIST=(list, []),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
    DEFAULT_FROM_EMAIL=(str, "no-reply@hel.fi"),
    VERSION=(str, None),
    DJANGO_LOG_LEVEL=(str, "INFO"),
    CSRF_TRUSTED_ORIGINS=(list, []),
    API_KEY_CUSTOM_HEADER=(str, "HTTP_X_API_KEY"),
    FIELD_ENCRYPTION_KEYS=(list, []),
    ENABLE_AUTOMATIC_ATTACHMENT_FILE_DELETION=(bool, True),
    ENABLE_SWAGGER_UI=(bool, True),
    ELASTIC_AUDIT_LOG_INDEX=(str, "logs-atv-audit"),
    ELASTIC_CREATE_DATA_STREAM=(bool, False),
    ELASTIC_HOST=(str, ""),
    ELASTIC_PORT=(int, 9200),
    ELASTIC_SSL=(bool, True),
    ELASTIC_USERNAME=(str, ""),
    ELASTIC_PASSWORD=(str, ""),
    ENABLE_SEND_AUDIT_LOG=(bool, False),
    CLEAR_AUDIT_LOG_ENTRIES=(bool, False),
    USE_X_FORWARDED_FOR=(bool, True),
    TOKEN_AUTH_ACCEPTED_AUDIENCE=(str, ""),
    TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=(str, ""),
    TOKEN_AUTH_REQUIRE_SCOPE=(bool, False),
    TOKEN_AUTH_AUTHSERVER_URL=(str, ""),
    CLAMAV_HOST=(str, "atv-clamav"),
)
if os.path.exists(env_file):
    env.read_env(env_file)


VERSION = env("VERSION")
if VERSION is None:
    try:
        VERSION = subprocess.check_output(
            ["git", "describe", "--always"], text=True
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        VERSION = None

sentry_sdk.init(
    dsn=env("SENTRY_DSN"),
    release=VERSION,
    environment=env("SENTRY_ENVIRONMENT"),
    integrations=[DjangoIntegration()],
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
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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

CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST")
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL")

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

AUDIT_LOG_ORIGIN = "atv"
ELASTIC_AUDIT_LOG_INDEX = env("ELASTIC_AUDIT_LOG_INDEX")
ELASTIC_HOST = env("ELASTIC_HOST")
ELASTIC_PORT = env("ELASTIC_PORT")
ELASTIC_SSL = env("ELASTIC_SSL")
ELASTIC_USERNAME = env("ELASTIC_USERNAME")
ELASTIC_PASSWORD = env("ELASTIC_PASSWORD")
ELASTIC_CREATE_DATA_STREAM = env("ELASTIC_CREATE_DATA_STREAM")
ENABLE_SEND_AUDIT_LOG = env("ENABLE_SEND_AUDIT_LOG")
CLEAR_AUDIT_LOG_ENTRIES = env("CLEAR_AUDIT_LOG_ENTRIES")

USE_X_FORWARDED_FOR = env("USE_X_FORWARDED_FOR")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "timestamped_named": {
            "format": "%(asctime)s %(name)s %(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "timestamped_named"}
    },
    "loggers": {"": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL")}},
}

# Malware Protection
CLAMAV_HOST = env("CLAMAV_HOST")
