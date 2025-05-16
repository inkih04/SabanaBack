from rest_framework import serializers
from issues.models import Comment

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # Incluimos los campos que queremos devolver
        fields = ['id', 'issue', 'user', 'text', 'published_at']
        # Marcamos todos excepto 'text' como read-only
        read_only_fields = ['id', 'issue', 'user', 'published_at']
