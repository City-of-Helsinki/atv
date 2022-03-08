from rest_framework import serializers

from documents.models import StatusHistory


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = ("document", "value", "timestamp")
        extra_kwargs = {"document": {"write_only": True}}
