from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from issues.models import Issue, Status, Priorities, Severities, Types

class IssueBulkItemSerializer(serializers.Serializer):
    subject     = serializers.CharField(max_length=200)

class IssueBulkResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'subject']


@extend_schema_serializer(exclude_fields=['status', 'priority', 'severity', 'issue_type', 'created_by', 'assigned_to'])
class IssueBulkCreateSerializer(serializers.Serializer):
    issues = IssueBulkItemSerializer(many=True)

    def create(self, validated_data):
        #Para probarlo sin token
        user = self.context['request'].user
        items = validated_data['issues']

        #todo : Aqui iran los valores por defecto

        #default_status   = Status.objects.get(nombre='Nuevo')
        #default_priority = Priorities.objects.get(nombre='Normal')
        #default_severity = Severities.objects.get(nombre='Medio')
        #default_type     = Types.objects.get(nombre='Tarea')

        to_create = []
        for it in items:
            to_create.append(
                Issue(
                    subject     = it['subject'],
                    description = "Bulk created issue",
                    status      = None,
                    priority    = None,
                    severity    = None,
                    issue_type  = None,
                    created_by  = user,
                )
            )

        # Creación masiva
        Issue.objects.bulk_create(to_create)

        # Recargar del DB para devolver IDs, timestamps, etc.
        return Issue.objects.filter(
            id__in=[i.id for i in to_create]
        )
