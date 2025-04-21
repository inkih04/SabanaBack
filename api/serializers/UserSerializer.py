from django.contrib.auth.models import User
from rest_framework import serializers

from issues.models import Status, Priorities, Types, Severities, Issue, Attachment, Comment, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']