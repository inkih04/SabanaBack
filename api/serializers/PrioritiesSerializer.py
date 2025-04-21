from rest_framework import serializers

from issues.models import Priorities


class PrioritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Priorities
        fields = ['id', 'nombre', 'color']