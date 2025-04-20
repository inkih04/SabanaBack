
from rest_framework import serializers

from api.serializers import UserSerializer
from issues.models import  Comment



class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'issue', 'user', 'text', 'published_at']
        read_only_fields = ['published_at', 'user']