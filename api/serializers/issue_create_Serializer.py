from rest_framework import serializers
from issues.models import Issue

class IssueCreateSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    status_name = serializers.CharField(required=False, allow_blank=True)
    severity_name = serializers.CharField(required=False, allow_blank=True)
    priority_name = serializers.CharField(required=False, allow_blank=True)
    issue_type_name = serializers.CharField(required=False, allow_blank=True)
    assigned_to_username = serializers.CharField(required=False, allow_blank=True)
    watchers_usernames = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True
    )
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        help_text="Lista de ficheros a adjuntar (opcional)"
    )

    class Meta:
        model = Issue
        fields = [
            'subject', 'description',
            'status_name', 'priority_name', 'severity_name', 'issue_type_name',
            'assigned_to_username', 'watchers_usernames', 'files'
        ]