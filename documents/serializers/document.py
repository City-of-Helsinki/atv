from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from utils.exceptions import ValidationError

from ..models import Document
from .attachment import AttachmentSerializer, CreateAnonymousAttachmentSerializer


class DocumentSerializer(serializers.ModelSerializer):
    """Basic "read" serializer for the Document model"""

    user_id = serializers.UUIDField(source="user.id", required=False, default=None)
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "created_at",
            "updated_at",
            "status",
            "type",
            "transaction_id",
            "user_id",
            "business_id",
            "tos_function_id",
            "tos_record_id",
            "metadata",
            "draft",
            "locked_after",
            "attachments",
        )


class CreateAnonymousDocumentSerializer(serializers.ModelSerializer):
    """Create a Document with Attachment for an anonymous user submitting the document
    through a Service authorized with an API key.

    Also handles the creation of the associated Attachments through
    `CreateAnonymousAttachmentSerializer`
    """

    attachments = serializers.ListField(child=serializers.FileField(), required=False)

    class Meta:
        model = Document
        fields = (
            "status",
            "type",
            "transaction_id",
            "business_id",
            "tos_function_id",
            "tos_record_id",
            "metadata",
            "draft",
            "locked_after",
            "attachments",
        )

    def validate(self, attrs):
        # Validate that no additional fields are being passed (to sanitize the input)
        if hasattr(self, "initial_data"):
            invalid_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if invalid_keys:
                raise ValidationError(
                    _("Got invalid input fields") + f": {', '.join(invalid_keys)}"
                )

        # Validate that no more than settings.MAX_FILE_UPLOAD_ALLOWED {default: 10} files
        # are uploaded on the same call
        if len(attrs.get("attachments")) > settings.MAX_FILE_UPLOAD_ALLOWED:
            raise serializers.ValidationError(
                _("File upload is limited to") + f" {settings.MAX_FILE_UPLOAD_ALLOWED}"
            )

        return attrs

    def create(self, validated_data):
        attachments = validated_data.pop("attachments")

        document = Document.objects.create(**validated_data)
        for attached_file in attachments:
            data = {
                "document": document.id,
                "file": attached_file,
                "media_type": attached_file.content_type,
            }
            attachment_serializer = CreateAnonymousAttachmentSerializer(data=data)
            attachment_serializer.is_valid(raise_exception=True)
            attachment_serializer.save()
        return document
