from django.contrib.auth.models import User
from rest_framework import serializers

from issues.models import Status, Priorities, Types, Severities, Issue, Attachment, Comment, Profile


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'nombre', 'slug', 'color']


class PrioritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Priorities
        fields = ['id', 'nombre', 'color']


class TypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = ['id', 'nombre', 'color']


class SeveritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Severities
        fields = ['id', 'nombre', 'color']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'biography', 'avatar']


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'issue', 'user', 'text', 'published_at']
        read_only_fields = ['published_at', 'user']


class IssueSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), source='status', write_only=True
    )
    priority = PrioritiesSerializer(read_only=True)
    priority_id = serializers.PrimaryKeyRelatedField(
        queryset=Priorities.objects.all(), source='priority', write_only=True
    )
    severity = SeveritiesSerializer(read_only=True)
    severity_id = serializers.PrimaryKeyRelatedField(
        queryset=Severities.objects.all(), source='severity', write_only=True
    )
    issue_type = TypesSerializer(read_only=True)
    issue_type_id = serializers.PrimaryKeyRelatedField(
        queryset=Types.objects.all(), source='issue_type', write_only=True
    )
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True, allow_null=True
    )
    created_by = UserSerializer(read_only=True)
    watchers = UserSerializer(read_only=True, many=True)
    watchers_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='watchers', many=True, write_only=True
    )
    attachment = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id', 'subject', 'description', 'created_at', 'due_date',
            'status', 'status_id',
            'priority', 'priority_id',
            'severity', 'severity_id',
            'issue_type', 'issue_type_id',
            'assigned_to', 'assigned_to_id',
            'created_by',
            'watchers', 'watchers_ids',
            'attachment', 'comments'
        ]
        read_only_fields = ['created_at', 'created_by']

    def create(self, validated_data):
        watchers = validated_data.pop('watchers', [])
        issue = Issue.objects.create(**validated_data, created_by=self.context['request'].user)
        if watchers:
            issue.watchers.set(watchers)
        return issue
