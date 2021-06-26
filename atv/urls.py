from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework import routers

from documents.api import DocumentViewSet

router = routers.DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="documents")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]


#
# Kubernetes liveness & readiness probes
#
def healthz(*args, **kwargs):
    return HttpResponse(status=200)


def readiness(*args, **kwargs):
    return HttpResponse(status=200)


urlpatterns += [path("healthz", healthz), path("readiness", readiness)]
