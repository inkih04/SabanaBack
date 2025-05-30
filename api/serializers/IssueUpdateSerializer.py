from django.contrib.auth.models import User
from rest_framework import serializers
from issues.models import (
    Issue, Status, Priorities, Severities, Types, Attachment
)


class IssueUpdateSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    status_name = serializers.CharField(required=False, allow_blank=True)
    severity_name = serializers.CharField(required=False, allow_blank=True)
    priority_name = serializers.CharField(required=False, allow_blank=True)
    issue_type_name = serializers.CharField(required=False, allow_blank=True)
    assigned_to_username = serializers.CharField(required=False, allow_blank=True)
    due_date = serializers.DateField(required=False, allow_null=True)

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
            'assigned_to_username', 'watchers_usernames', 'files', 'due_date'
        ]

    def validate_due_date(self, value):
        """
        Validación personalizada para due_date.
        - Si viene una cadena vacía, devuelve None (para quitar la fecha)
        - Si viene None, devuelve None
        - Si viene una fecha válida, la devuelve
        """
        if value == "" or value is None:
            return None
        return value

    def to_internal_value(self, data):
        """
        Procesa los datos antes de la validación.
        Convierte cadenas vacías de due_date a None.
        """
        # Hacemos una copia para no modificar los datos originales
        data = data.copy() if hasattr(data, 'copy') else dict(data)

        # Si due_date viene como cadena vacía, lo convertimos a None
        if 'due_date' in data and data['due_date'] == '':
            data['due_date'] = None

        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        # Extraemos los mismos campos que en create…
        status_name = validated_data.pop('status_name', None)
        priority_name = validated_data.pop('priority_name', None)
        severity_name = validated_data.pop('severity_name', None)
        issue_type_name = validated_data.pop('issue_type_name', None)
        assigned_username = validated_data.pop('assigned_to_username', None)
        watchers_usernames = validated_data.pop('watchers_usernames', [])
        files = validated_data.pop('files', [])

        # Si vienen, resolvemos o levantamos error
        if status_name is not None:
            try:
                instance.status = Status.objects.get(nombre=status_name)
            except Status.DoesNotExist:
                raise serializers.ValidationError({
                    'status_name': f"El status '{status_name}' no existe."
                })
        if priority_name is not None:
            try:
                instance.priority = Priorities.objects.get(nombre=priority_name)
            except Priorities.DoesNotExist:
                raise serializers.ValidationError({
                    'priority_name': f"La prioridad '{priority_name}' no existe."
                })
        if severity_name is not None:
            try:
                instance.severity = Severities.objects.get(nombre=severity_name)
            except Severities.DoesNotExist:
                raise serializers.ValidationError({
                    'severity_name': f"La severidad '{severity_name}' no existe."
                })
        if issue_type_name is not None:
            try:
                instance.issue_type = Types.objects.get(nombre=issue_type_name)
            except Types.DoesNotExist:
                raise serializers.ValidationError({
                    'issue_type_name': f"El tipo de issue '{issue_type_name}' no existe."
                })

        # Cambios de subject/description sólo si vienen
        if 'subject' in validated_data:
            instance.subject = validated_data['subject']
        if 'description' in validated_data:
            instance.description = validated_data['description']

        # Manejo especial para due_date
        if 'due_date' in validated_data:
            instance.due_date = validated_data['due_date']  # Ya será None si vino vacío

        # Asignar assigned_to si se pasó
        if assigned_username:
            try:
                instance.assigned_to = User.objects.get(username=assigned_username)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'assigned_to_username': f"El usuario '{assigned_username}' no existe."
                })

        instance.save()

        # Watchers (igual que en create)
        if len(watchers_usernames) == 1 and isinstance(watchers_usernames[0], str) and ',' in watchers_usernames[0]:
            watchers_usernames = [u.strip() for u in watchers_usernames[0].split(',') if u.strip()]
        for username in watchers_usernames:
            try:
                watcher = User.objects.get(username=username)
                instance.watchers.add(watcher)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'watchers_usernames': f"El usuario '{username}' no existe."
                })

        # Archivos nuevos
        for f in files:
            Attachment.objects.create(issue=instance, file=f)

        return instance