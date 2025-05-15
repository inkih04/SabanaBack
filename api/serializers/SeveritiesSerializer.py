from rest_framework import serializers

from issues.models import Severities



class SeveritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Severities
        fields = ['id', 'nombre', 'color']