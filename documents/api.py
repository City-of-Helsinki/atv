from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from services.models import Service, ServiceAPIKey
from services.permissions import HasServiceAPIKey

from .models import Attachment, Document
from .serializers import (
    AttachmentSerializer,
    CreateAnonymousDocumentSerializer,
    DocumentSerializer,
)


class AttachmentViewSet(ModelViewSet, NestedViewSetMixin):
    queryset = Attachment.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = AttachmentSerializer


class DocumentViewSet(ModelViewSet):
    queryset = Document.objects.all()
    permission_classes = [HasServiceAPIKey | IsAdminUser]
    parser_classes = [MultiPartParser]
    serializer_class = DocumentSerializer

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        try:
            key = request.META.get(settings.API_KEY_CUSTOM_HEADER)
            service_key = ServiceAPIKey.objects.get_from_key(key)
            service = service_key.service
        except (ServiceAPIKey.DoesNotExist, Service.DoesNotExist):
            raise NotAuthenticated()

        data = request.data

        serializer = CreateAnonymousDocumentSerializer(data=data)

        # If the data is not valid, it will raise a ValidationError and return Bad Request
        serializer.is_valid(raise_exception=True)

        document = serializer.save(service=service)

        return Response(
            data=DocumentSerializer(document, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
