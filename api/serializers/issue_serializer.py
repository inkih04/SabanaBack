from rest_framework import serializers
from issues.models import Issue, Comment, Attachment, Status, Priorities, Severities, Types
from django.contrib.auth.models import User

class IssueCommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user']


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']


class IssueSerializer(serializers.ModelSerializer):
    status = serializers.SlugRelatedField(read_only=True, slug_field='nombre')
    priority = serializers.SlugRelatedField(read_only=True, slug_field='nombre')
    severity = serializers.SlugRelatedField(read_only=True, slug_field='nombre')
    issue_type = serializers.SlugRelatedField(read_only=True, slug_field='nombre')
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    watchers = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='username'
    )
    attachment = AttachmentSerializer(many=True, read_only=True)
    comments = IssueCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id', 'subject', 'description', 'created_at', 'due_date',
            'status', 'priority', 'severity', 'issue_type',
            'created_by', 'assigned_to', 'watchers',
            'attachment', 'comments',
        ]
