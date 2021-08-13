from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework_extensions.routers import ExtendedSimpleRouter

from documents.api import AttachmentViewSet, DocumentViewSet

router = ExtendedSimpleRouter()

router.register(r"documents", DocumentViewSet, basename="documents").register(
    r"attachments",
    AttachmentViewSet,
    basename="documents-attachments",
    parents_query_lookups=["document"],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include(router.urls)),
]


#
# Kubernetes liveness & readiness probes
#
def healthz(*args, **kwargs):
    return HttpResponse(status=200)


def readiness(*args, **kwargs):
    return HttpResponse(status=200)


urlpatterns += [path("healthz", healthz), path("readiness", readiness)]
