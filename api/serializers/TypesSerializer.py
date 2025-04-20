from rest_framework import serializers

from issues.models import Types


class TypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = ['id', 'nombre', 'color']