import re
from rest_framework import serializers
from issues.models import Types


class TypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = ['id', 'nombre', 'color']

    def validate_color(self, value):
        # Valida que el color sea un string hexadecimal válido (#RRGGBB)
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError("El color debe tener el formato hexadecimal '#RRGGBB'.")
        return value