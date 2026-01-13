from rest_framework import serializers

from users.models import User


class GDPRUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        )
