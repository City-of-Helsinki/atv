from rest_framework import serializers

from services.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("name", "display_names", "service_link")
