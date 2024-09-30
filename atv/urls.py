import pyclamd
import threading
import time
from atv import __version__
from django.conf import settings
from django.contrib import admin
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_extensions.routers import ExtendedSimpleRouter

from documents.api import AttachmentViewSet, DocumentViewSet
from documents.api.viewsets import (
    DocumentMetadataViewSet,
    DocumentStatisticsViewSet,
    DocumentStatusActivityViewSet,
    GDPRDataViewSet,
)

router = ExtendedSimpleRouter()
document_router = router.register(r"documents", DocumentViewSet, basename="documents")
document_router.register(
    r"attachments",
    AttachmentViewSet,
    basename="documents-attachments",
    parents_query_lookups=["document_id"],
)
document_router.register(
    r"status",
    DocumentStatusActivityViewSet,
    basename="document-status-history",
    parents_query_lookups=["document_id"],
)
router.register(r"userdocuments", DocumentMetadataViewSet, basename="userdocuments")
router.register(r"gdpr-api", GDPRDataViewSet, basename="gdpr-api")
router.register(
    r"statistics", DocumentStatisticsViewSet, basename="document-statistics"
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include(router.urls)),
]

if settings.SENTRY_DEBUG:
    urlpatterns += [
        path("sentry-debug/", lambda a: 1 / 0),
    ]


if settings.ENABLE_SWAGGER_UI:
    urlpatterns += [
        path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "v1/schema/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger",
        ),
        path(
            "v1/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

#
# Kubernetes liveness & readiness probes
#

# Global variable to store the health check results
health_status = {
    "db": {"message": "Initializing"},
    "clamav": {"message": "Initializing"}
}

def check_db_connection():
    global health_status
    while True:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["db"] = {"message": "OK"}
        except Exception as ex:
            health_status["db"] = {"error": str(ex)}
        time.sleep(300)  # Sleep for 5 minutes

def check_clamav_connection():
    global health_status
    while True:
        try:
            cd = pyclamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST)
            cd.ping()
            health_status["clamav"] = {"message": "OK"}
        except Exception as ex:
            health_status["clamav"] = {"error": str(ex)}
        time.sleep(300)  # Sleep for 5 minutes

# Start the health check threads
threading.Thread(target=check_db_connection, daemon=True).start()
threading.Thread(target=check_clamav_connection, daemon=True).start()

def healthz(*args, **kwargs):
    response_data = {
        "packageVersion": __version__,
        "commitHash": settings.BUILD_COMMIT,
        "buildTime": settings.APP_BUILDTIME,
        "status": {
            "message": {},
            "error": {}
        }
    }

    for key, status in health_status.items():
        if "message" in status and status["message"] == "OK":
            response_data["status"]["message"][key] = status["message"]
        else:
            response_data["status"]["error"][key] = status.get("error", "Unknown error")

    status_code = 200 if all("message" in status and status["message"] == "OK" for status in health_status.values()) else 250
    return JsonResponse(response_data, status=status_code)

def readiness(*args, **kwargs):
    return HttpResponse(status=200)


urlpatterns += [path("healthz", healthz), path("readiness", readiness)]
