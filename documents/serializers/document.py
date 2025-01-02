from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from helusers.utils import uuid_to_username
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from atv.exceptions import (
    DocumentLockedException,
    InvalidFieldException,
    MaximumFileCountExceededException,
)
from services.models import ServiceAPIKey
from services.serializers.service import ServiceSerializer
from users.models import User

from ..models import Document
from .attachment import (
    AttachmentNameSerializer,
    AttachmentSerializer,
    CreateAttachmentSerializer,
)
from .status_history import StatusHistorySerializer


def status_to_representation(representation):
    status_timestamp = representation.pop("status_timestamp")
    status_display_values = representation.pop("status_display_values")
    # Pick first status history object to current status
    status_histories = representation["status_histories"]
    representation["status"] = (
        status_histories[0]
        if len(status_histories) != 0
        else {
            "value": representation["status"],
            "status_display_values": status_display_values,
            "timestamp": status_timestamp,
        }
    )
    return representation


class DocumentStatisticsSerializer(serializers.ModelSerializer):
    service = serializers.CharField(
        source="service.name", required=False, read_only=True
    )
    attachments = AttachmentNameSerializer(many=True)
    # Attachment count included here just for clarity. Field is added to
    # response body in to_representation
    attachment_count = serializers.HiddenField(default=0)
    user_id = serializers.UUIDField(source="user.uuid", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "created_at",
            "user_id",
            "service",
            "transaction_id",
            "type",
            "human_readable_type",
            "status",
            "deletable",
            "attachments",
            "attachment_count",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Calculate attachment count here instead of aggregating it to queryset
        # for performance reasons
        representation["attachment_count"] = len(representation["attachments"])
        return representation


class GDPRDocumentSerializer(serializers.ModelSerializer):
    service = serializers.CharField(
        source="service.name", required=False, read_only=True
    )
    attachments = AttachmentNameSerializer(many=True, read_only=True)
    attachment_count = serializers.IntegerField()
    user_id = serializers.UUIDField(source="user.uuid", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "created_at",
            "user_id",
            "service",
            "type",
            "human_readable_type",
            "deletable",
            "delete_after",
            "attachment_count",
            "attachments",
        )


class GDPRSerializer(serializers.Serializer):  # noqa
    data = serializers.SerializerMethodField()

    def get_data(self, documents_qs):
        documents_qs = documents_qs.annotate(attachment_count=Count("attachments"))
        total = documents_qs.count()
        deletable = documents_qs.filter(deletable=True).count()

        stats = {
            "total_deletable": deletable,
            "total_undeletable": total - deletable,
            "documents": GDPRDocumentSerializer(documents_qs, many=True).data,
        }
        return stats


class DocumentMetadataSerializer(serializers.ModelSerializer):
    status_histories = StatusHistorySerializer(many=True, read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "type",
            "human_readable_type",
            "created_at",
            "updated_at",
            "service",
            "status",
            "status_display_values",
            "status_timestamp",
            "status_histories",
            "delete_after",
            "document_language",
            "content_schema_url",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return status_to_representation(rep)


class DocumentSerializer(serializers.ModelSerializer):
    """Basic "read" serializer for the Document model."""

    user_id = serializers.UUIDField(
        source="user.uuid", required=False, default=None, read_only=True
    )
    attachments = AttachmentSerializer(many=True, required=False, read_only=True)
    content = serializers.JSONField(
        required=True, decoder=None, encoder=DjangoJSONEncoder
    )
    service = serializers.CharField(
        source="service.name", required=False, read_only=True
    )
    status_histories = StatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "created_at",
            "updated_at",
            "status",
            "status_display_values",
            "status_timestamp",
            "status_histories",
            "type",
            "human_readable_type",
            "service",
            "user_id",
            "transaction_id",
            "business_id",
            "tos_function_id",
            "tos_record_id",
            "metadata",
            "content",
            "draft",
            "locked_after",
            "deletable",
            "delete_after",
            "document_language",
            "content_schema_url",
            "attachments",
        )

    def update(self, document, validated_data):
        # If the document has been locked, no further updates are allowed
        if document.locked_after and document.locked_after <= now():
            raise DocumentLockedException()
        # Deletable field can be changed from True to False but not the other
        # way
        if validated_data.get("deletable") is True and not document.deletable:
            raise PermissionDenied(
                detail="Field 'deletable' can't be changed if set to False"
            )
        user_id = self.initial_data.get("user_id", None)
        if user_id:
            if document.user_id and not isinstance(
                self.context["request"].auth, ServiceAPIKey
            ):
                raise PermissionDenied(
                    detail="Document owner can be changed only by API key users.",
                    code="invalid field: user_id",
                )

            user, created = User.objects.get_or_create(
                uuid=user_id, defaults={"username": uuid_to_username(user_id)}
            )
            document.user = user
            document.save()

        return super().update(document, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return status_to_representation(representation)


class CreateAnonymousDocumentSerializer(serializers.ModelSerializer):
    """Create a Document with Attachment for an anonymous user submitting the
    document through a Service authorized with an API key.

    Also handles the creation of the associated Attachments through
    `CreateAttachmentSerializer`.
    """

    user_id = serializers.UUIDField(source="user.uuid", required=False, default=None)
    attachments = serializers.ListField(child=serializers.FileField(), required=False)
    content = serializers.JSONField(
        required=True, decoder=None, encoder=DjangoJSONEncoder
    )

    class Meta:
        model = Document
        fields = (
            "status",
            "status_display_values",
            "type",
            "human_readable_type",
            "user_id",
            "transaction_id",
            "business_id",
            "tos_function_id",
            "tos_record_id",
            "metadata",
            "content",
            "draft",
            "locked_after",
            "deletable",
            "delete_after",
            "document_language",
            "content_schema_url",
            "attachments",
        )

    def validate(self, attrs):
        # Validate that no additional fields are being passed (to sanitize the
        # input)
        if hasattr(self, "initial_data"):
            invalid_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if invalid_keys:
                raise InvalidFieldException(
                    detail=_("Got invalid input fields: {list_of_fields}").format(
                        list_of_fields=", ".join(invalid_keys)
                    )
                )

        # Validate that no more than settings.MAX_FILE_UPLOAD_ALLOWED files
        # are uploaded on the same call
        if len(attrs.get("attachments", [])) > settings.MAX_FILE_UPLOAD_ALLOWED:
            raise MaximumFileCountExceededException()

        return attrs

    def create(self, validated_data):
        attachments = validated_data.pop("attachments", [])

        document = Document.objects.create(**validated_data)
        for attached_file in attachments:
            data = {
                "document": document.id,
                "file": attached_file,
                "media_type": attached_file.content_type,
            }
            attachment_serializer = CreateAttachmentSerializer(data=data)
            attachment_serializer.is_valid(raise_exception=True)
            attachment_serializer.save()
        return document
