from django.contrib.auth.models import User
from rest_framework import serializers

from issues.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']