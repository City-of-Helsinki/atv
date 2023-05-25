from rest_framework import serializers

from atv.exceptions import InvalidFieldException
from documents.models import Activity, StatusHistory
from documents.serializers.activity import ActivitySerializer


class CreateStatusHistorySerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(required=False)

    class Meta:
        model = StatusHistory
        fields = (
            "document",
            "value",
            "status_display_values",
            "timestamp",
            "activity",
        )

    def validate(self, attrs):
        if not (attrs.get("value") or attrs.get("activity")):
            raise InvalidFieldException(
                detail="Value of new status, or activity structure is required."
            )

        return super().validate(attrs)

    def create(self, validated_data):
        document = validated_data["document"]
        activity = validated_data.get("activity")
        status_value = validated_data.get("value")
        document_changed = False

        current_status = StatusHistory.objects.filter(document=document).first()
        status_display_values = validated_data.get("status_display_values", {})
        if current_status:
            if current_status.value != status_value and status_value:
                status = StatusHistory.objects.create(
                    document=document,
                    value=status_value,
                    status_display_values=status_display_values,
                )
                document_changed = True
            else:
                status = current_status
        else:
            status = StatusHistory.objects.create(
                document=document,
                value=status_value,
                status_display_values=status_display_values,
            )
            document_changed = True

        if activity and status:
            Activity.objects.create(**activity, status=status)
            document_changed = True

        # Save document so updated_at field represents latest change's timestamp
        if document_changed:
            document.save()

        return status, document_changed


class StatusHistorySerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, required=False)

    class Meta:
        model = StatusHistory
        fields = ("value", "status_display_values", "timestamp", "activities")
