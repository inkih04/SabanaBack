from django.contrib.auth.models import User
from rest_framework import serializers
from issues.models import (
    Issue, Status, Priorities, Severities, Types, Attachment
)

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

    def create(self, validated_data):
        # Extraemos y eliminamos los campos "name" / "usernames" / "files"
        status_name = validated_data.pop('status_name', None) or 'New'
        priority_name = validated_data.pop('priority_name', None) or 'Medium'
        severity_name = validated_data.pop('severity_name', None) or 'Normal'
        issue_type_name = validated_data.pop('issue_type_name', None) or 'Bug'
        assigned_username = validated_data.pop('assigned_to_username', None)
        watchers_usernames = validated_data.pop('watchers_usernames', [])
        files = validated_data.pop('files', [])

        # Resolvemos o creamos instancias relacionales
        try:
            status_obj = Status.objects.get(nombre=status_name)
        except Status.DoesNotExist:
            raise serializers.ValidationError({
                'status_name': f"El status '{status_name}' no existe."
            })

        try:
            priority_obj = Priorities.objects.get(nombre=priority_name)
        except Priorities.DoesNotExist:
            raise serializers.ValidationError({
                'priority_name': f"La prioridad '{priority_name}' no existe."
            })

        try:
            severity_obj = Severities.objects.get(nombre=severity_name)
        except Severities.DoesNotExist:
            raise serializers.ValidationError({
                'severity_name': f"La severidad '{severity_name}' no existe."
            })

        try:
            type_obj = Types.objects.get(nombre=issue_type_name)
        except Types.DoesNotExist:
            raise serializers.ValidationError({
                'issue_type_name': f"El tipo de issue '{issue_type_name}' no existe."
            })

        # Creamos el Issue
        issue = Issue.objects.create(
            subject=validated_data['subject'],
            description=validated_data['description'],
            status=status_obj,
            priority=priority_obj,
            severity=severity_obj,
            issue_type=type_obj,
            created_by=self.context['request'].user,
            # assigned_to puede quedarse en null si no viene
        )

        # Asignar "assigned_to" si se pasó username
        if assigned_username:
            try:
                user = User.objects.get(username=assigned_username)
                issue.assigned_to = user
                issue.save()
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'assigned_to_username': f"El usuario '{assigned_username}' no existe."
                })

        # Asignar watchers
        if len(watchers_usernames) == 1 and isinstance(watchers_usernames[0], str) and ',' in watchers_usernames[0]:
            watchers_usernames = [
                u.strip() for u in watchers_usernames[0].split(',') if u.strip()
            ]

        for username in watchers_usernames:
            try:
                watcher = User.objects.get(username=username)
                issue.watchers.add(watcher)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'watchers_usernames': f"El usuario '{username}' no existe."
                })

        # Adjuntar ficheros
        for f in files:
            Attachment.objects.create(issue=issue, file=f)

        return issue
