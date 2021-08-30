from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from atv.decorators import service_api_key_required, staff_required
from services.enums import ServicePermissions
from services.models import Service, ServiceAPIKey

from .models import Attachment, Document
from .serializers import (
    AttachmentSerializer,
    CreateAnonymousDocumentSerializer,
    DocumentSerializer,
)


class AttachmentViewSet(ModelViewSet, NestedViewSetMixin):
    permission_classes = [IsAdminUser]
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        """
        Only allow for the user to see Attachments that belong to their Documents
        or their Service.

        If the user is:
            - superuser, they can see everything
            - staff, they can see only Attachments for Documents of their Service
            - authenticated, they can see only their own Attachments
            - anonymous (no valid authentication), they can't see anything
        """
        user = self.request.user

        # If the user is a superuser, return the whole set
        if user.is_superuser:
            return Attachment.objects.all()

        # If the user is anonymous, don't return anything,
        # even if they're associated to a Service.
        if user.is_anonymous:
            return Attachment.objects.none()

        filters = {}

        # Filter the Documents only for the user's Service
        if service := self.request.service:
            filters["document__service"] = service

        # If the user doesn't have permissions to view that Service,
        # only show the Documents that belong to them
        if not user.has_perm(
            ServicePermissions.VIEW_ATTACHMENTS.value, filters["service"]
        ):
            filters = {"document__user_id": user.id}

        return Attachment.objects.filter(**filters)


class DocumentViewSet(ModelViewSet):
    parser_classes = [MultiPartParser]
    serializer_class = DocumentSerializer
    # Permission checking is done by the decorators on a method basis
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Only allow for the user to see Documents that belong to them or their Service.

        If the user is:
            - superuser, they can see everything
            - staff, they can see only Documents for their Service
            - authenticated, they can see only their own Documents
            - anonymous (no valid authentication), they can't see anything
        """
        user = self.request.user

        # If the user is a superuser, return the whole set
        if user.is_superuser:
            return Document.objects.all()

        # If the user is anonymous, don't return anything,
        # even if they're associated to a Service.
        if user.is_anonymous:
            return Document.objects.none()

        filters = {}

        # Filter the Documents only for the user's Service
        if service := self.request.service:
            filters["service"] = service

        # If the user doesn't have permissions to view that Service,
        # only show the Documents that belong to them
        if not user.has_perm(
            ServicePermissions.VIEW_DOCUMENTS.value, filters["service"]
        ):
            filters = {"user_id": user.id}

        return Document.objects.filter(**filters)

    @staff_required(required_permission=ServicePermissions.VIEW_DOCUMENTS)
    def list(self, request, *args, **kwargs):
        return super(DocumentViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic()
    @service_api_key_required()
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
