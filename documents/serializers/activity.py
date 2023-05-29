import jsonschema
from jsonschema.exceptions import ValidationError as JSONValidationError
from rest_framework import serializers

from atv.exceptions import InvalidFieldException
from documents.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    title = serializers.JSONField(required=True)
    message = serializers.JSONField(required=True)
    show_to_user = serializers.BooleanField(required=False)

    class Meta:
        model = Activity
        fields = (
            "title",
            "message",
            "activity_links",
            "activity_timestamp",
            "show_to_user",
        )
        extra_kwargs = {"status": {"write_only": True}}

    def validate(self, attrs):
        activity_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "object"},
                "message": {"type": "object"},
                "activity_links": {"type": "object"},
                "show_to_user": {"type": "boolean"},
            },
            "required": ["title", "message"],
            "additionalProperties": False,
        }
        try:
            jsonschema.validate(instance=attrs, schema=activity_schema)
        except JSONValidationError as e:
            raise InvalidFieldException(detail=f"{e.path[0]}: {e.message}")

        return attrs
