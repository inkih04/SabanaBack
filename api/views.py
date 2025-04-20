# api/views.py
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, filters
from issues.models import Issue, Attachment, Comment, Status, Types, Priorities, Severities
from .serializers import (
    IssueSerializer, AttachmentSerializer, CommentSerializer,
    StatusSerializer, TypesSerializer, PrioritiesSerializer, SeveritiesSerializer
)


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'severity', 'issue_type', 'created_by', 'assigned_to']

    ordering_fields = ['created_at', 'updated_at', 'priority', 'status', 'severity', 'issue_type', 'created_by',
                       'assigned_to']
    ordering = ['-created_at']

    @swagger_auto_schema(
        manual_parameters=[
            # Documentación de los filterset_fields
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description=(
                        "Campo(s) por los que ordenar. Se admiten varios "
                        "separados por coma. Para orden descendente, "
                        "anteponer “-”.\n\n"
                        "**Campos válidos:** created_at, updated_at, priority, status, "
                        "severity, issue_type, created_by, assigned_to\n\n"
                        "Ejemplo: `ordering=-priority,created_at` \n\n"
                ),
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filtrar por ID de estado",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'priority',
                openapi.IN_QUERY,
                description="Filtrar por ID de prioridad",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'severity',
                openapi.IN_QUERY,
                description ="Filtrar por ID de severidad",
                type = openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'issue_type',
                openapi.IN_QUERY,
                description="Filtrar por ID de tipo de issue",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'created_by',
                openapi.IN_QUERY,
                description="Filtrar por ID del usuario creador",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'assigned_to',
                openapi.IN_QUERY,
                description="Filtrar por ID del usuario asignado",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'unassigned',
                openapi.IN_QUERY,
                description="Filtrar issues sin asignar",
                type=openapi.TYPE_BOOLEAN
            ),
            ]
            )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Issue.objects.all()


        # Filtro para issues sin asignar
        unassigned = self.request.query_params.get('unassigned')
        if unassigned == 'true':
            queryset = queryset.filter(assigned_to=None)



        return queryset




class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


