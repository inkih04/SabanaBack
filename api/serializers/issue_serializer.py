from rest_framework import serializers
from django.contrib.auth.models import User

from .StatusSerializer import StatusSerializer
from .PrioritiesSerializer import PrioritiesSerializer
from .TypesSerializer import TypesSerializer
from .SeveritiesSerializer import SeveritiesSerializer
from .UserSerializer import UserSerializer
from .AttachmentSerializer import AttachmentSerializer
from .CommentSerializer import CommentSerializer
from issues.models import Status, Priorities, Types, Severities, Issue, Attachment, Comment, Profile



class IssueSerializer(serializers.ModelSerializer):
    # Campos existentes
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), source='status', write_only=True, required=False
    )
    status_name = serializers.CharField(write_only=True, required=False)

    priority = PrioritiesSerializer(read_only=True)
    priority_id = serializers.PrimaryKeyRelatedField(
        queryset=Priorities.objects.all(), source='priority', write_only=True, required=False
    )
    priority_name = serializers.CharField(write_only=True, required=False)

    severity = SeveritiesSerializer(read_only=True)
    severity_id = serializers.PrimaryKeyRelatedField(
        queryset=Severities.objects.all(), source='severity', write_only=True, required=False
    )
    severity_name = serializers.CharField(write_only=True, required=False)

    issue_type = TypesSerializer(read_only=True)
    issue_type_id = serializers.PrimaryKeyRelatedField(
        queryset=Types.objects.all(), source='issue_type', write_only=True, required=False
    )
    issue_type_name = serializers.CharField(write_only=True, required=False)

    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True, required=False, allow_null=True
    )
    assigned_to_username = serializers.CharField(write_only=True, required=False, allow_null=True)

    created_by = UserSerializer(read_only=True)
    watchers = UserSerializer(read_only=True, many=True)
    watchers_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='watchers', many=True, write_only=True, required=False
    )
    watchers_usernames = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    attachment = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id', 'subject', 'description', 'created_at', 'due_date',
            'status', 'status_id', 'status_name',
            'priority', 'priority_id', 'priority_name',
            'severity', 'severity_id', 'severity_name',
            'issue_type', 'issue_type_id', 'issue_type_name',
            'assigned_to', 'assigned_to_id', 'assigned_to_username',
            'created_by',
            'watchers', 'watchers_ids', 'watchers_usernames',
            'attachment', 'comments'
        ]
        read_only_fields = ['created_at', 'created_by']

    def validate(self, data):
        # Procesamos campos por nombre para Status
        if 'status_name' in self.initial_data and not data.get('status'):
            try:
                status = Status.objects.get(nombre=self.initial_data['status_name'])
                data['status'] = status
            except Status.DoesNotExist:
                raise serializers.ValidationError(
                    {"status_name": f"No existe Status con nombre '{self.initial_data['status_name']}'"})

        # Procesamos campos por nombre para Priority
        if 'priority_name' in self.initial_data and not data.get('priority'):
            try:
                priority = Priorities.objects.get(nombre=self.initial_data['priority_name'])
                data['priority'] = priority
            except Priorities.DoesNotExist:
                raise serializers.ValidationError(
                    {"priority_name": f"No existe Priority con nombre '{self.initial_data['priority_name']}'"})

        # Procesamos campos por nombre para Severity
        if 'severity_name' in self.initial_data and not data.get('severity'):
            try:
                severity = Severities.objects.get(nombre=self.initial_data['severity_name'])
                data['severity'] = severity
            except Severities.DoesNotExist:
                raise serializers.ValidationError(
                    {"severity_name": f"No existe Severity con nombre '{self.initial_data['severity_name']}'"})

        # Procesamos campos por nombre para Type
        if 'issue_type_name' in self.initial_data and not data.get('issue_type'):
            try:
                issue_type = Types.objects.get(nombre=self.initial_data['issue_type_name'])
                data['issue_type'] = issue_type
            except Types.DoesNotExist:
                raise serializers.ValidationError(
                    {"issue_type_name": f"No existe Type con nombre '{self.initial_data['issue_type_name']}'"})

        # Procesamos campo por username para assigned_to
        if 'assigned_to_username' in self.initial_data and self.initial_data['assigned_to_username']:
            try:
                user = User.objects.get(username=self.initial_data['assigned_to_username'])
                data['assigned_to'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({
              "assigned_to_username": f"No existe usuario con username '{self.initial_data['assigned_to_username']}'"})

        # Procesamos campos por username para watchers
        if 'watchers_usernames' in self.initial_data:
            usernames = self.initial_data['watchers_usernames']
            watchers = []
            for username in usernames:
                try:
                    user = User.objects.get(username=username)
                    watchers.append(user)
                except User.DoesNotExist:
                    raise serializers.ValidationError(
                        {"watchers_usernames": f"No existe usuario con username '{username}'"})
            if watchers:
                data['watchers'] = watchers

        return data

    def create(self, validated_data):
        watchers = validated_data.pop('watchers', [])
        issue = Issue.objects.create(**validated_data, created_by=self.context['request'].user)
        if watchers:
            issue.watchers.set(watchers)
        return issue