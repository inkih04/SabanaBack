from rest_framework import serializers

from issues.models import Status



class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'nombre', 'slug', 'color']