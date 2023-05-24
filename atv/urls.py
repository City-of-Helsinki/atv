from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
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

router.register(r"documents", DocumentViewSet, basename="documents").register(
    r"attachments",
    AttachmentViewSet,
    basename="documents-attachments",
    parents_query_lookups=["document_id"],
)
router.register(r"documents", DocumentViewSet, basename="documents").register(
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


def healthz(*args, **kwargs):
    return HttpResponse(status=200)


def readiness(*args, **kwargs):
    return HttpResponse(status=200)


urlpatterns += [path("healthz", healthz), path("readiness", readiness)]
