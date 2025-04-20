from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, filters
from issues.models import Issue
from ..serializers import IssueSerializer

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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'subject': openapi.Schema(type=openapi.TYPE_STRING, description='Asunto del issue'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción detallada'),
                'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date',
                                           description='Fecha límite (YYYY-MM-DD)'),
                # Campos simplificados por nombre
                'status_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del status'),
                'priority_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la prioridad'),
                'severity_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la severidad'),
                'issue_type_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del tipo de issue'),
                'assigned_to_username': openapi.Schema(type=openapi.TYPE_STRING,
                                                       description='Nombre de usuario asignado'),
                'watchers_usernames': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='Lista de nombres de usuario observadores'
                ),
            },
            required=['subject', 'description']  # Solo estos campos son realmente obligatorios
        )
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

        # Documentación para el método UPDATE (PUT)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'subject': openapi.Schema(type=openapi.TYPE_STRING, description='Asunto del issue'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción detallada'),
                'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date',
                                           description='Fecha límite (YYYY-MM-DD)'),
                # Campos simplificados por nombre
                'status_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del status'),
                'priority_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la prioridad'),
                'severity_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la severidad'),
                'issue_type_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del tipo de issue'),
                'assigned_to_username': openapi.Schema(type=openapi.TYPE_STRING,
                                                       description='Nombre de usuario asignado'),
                'watchers_usernames': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='Lista de nombres de usuario observadores'
                ),
            },
            required=['subject', 'description']  # En un PUT normalmente todos los campos son requeridos
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

        # Documentación para el método PARTIAL_UPDATE (PATCH)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'subject': openapi.Schema(type=openapi.TYPE_STRING, description='Asunto del issue'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción detallada'),
                'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date',
                                           description='Fecha límite (YYYY-MM-DD)'),
                # Campos simplificados por nombre
                'status_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del status'),
                'priority_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la prioridad'),
                'severity_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la severidad'),
                'issue_type_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del tipo de issue'),
                'assigned_to_username': openapi.Schema(type=openapi.TYPE_STRING,
                                                       description='Nombre de usuario asignado'),
                'watchers_usernames': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='Lista de nombres de usuario observadores'
                ),
            },
            # En PATCH ningún campo es requerido, ya que es para actualizaciones parciales
        )
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Issue.objects.all()


        # Filtro para issues sin asignar
        unassigned = self.request.query_params.get('unassigned')
        if unassigned == 'true':
            queryset = queryset.filter(assigned_to=None)



        return queryset