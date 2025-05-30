from absl.testing.parameterized import parameters
from django.db.models import Q
from django.http import QueryDict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema_view, extend_schema,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)

from issues.models import Issue, Attachment
from ..filters import IssueFilter
from ..serializers import IssueSerializer, AttachmentSerializer, IssueBulkCreateSerializer, IssueCreateSerializer, \
    IssueUpdateSerializer
from ..serializers.IssueUpdateSerializer import IssueUpdateSerializer
from ..serializers.issueBulk_serializer import IssueBulkResponseSerializer


class AttachmentUploadSerializer(serializers.Serializer):
    file = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        allow_empty=False,
        help_text="Lista de archivos a adjuntar"
    )


def normalize_request_data(request_data, request_files=None):
    """
    Normaliza los datos de request para manejar tanto JSON como form-data
    """
    if isinstance(request_data, QueryDict):
        # Es form-data (multipart/form-data)
        qd = request_data.copy()
        qd._mutable = True

        # Manejo especial para watchers_usernames en form-data
        if hasattr(request_data, 'getlist'):
            raw = request_data.getlist('watchers_usernames')
            if raw:
                qd.setlist('watchers_usernames', [u.strip() for u in raw if isinstance(u, str) and u.strip()])
            else:
                qd.pop('watchers_usernames', None)

        # Eliminar 'files' si no hay archivos reales
        if 'files' in qd and not request_files:
            qd.pop('files')

        # Convertir QueryDict a dict normal
        clean_data = {}
        for key, vals in qd.lists():
            if key in ('watchers_usernames', 'watchers_ids', 'files'):
                clean_data[key] = vals
            else:
                clean_data[key] = vals[0] if len(vals) == 1 else vals
    else:
        # Es JSON o dict normal
        clean_data = request_data.copy()

        # Procesar watchers_usernames para JSON
        if 'watchers_usernames' in clean_data:
            watchers = clean_data['watchers_usernames']
            if isinstance(watchers, list):
                clean_data['watchers_usernames'] = [u.strip() for u in watchers if isinstance(u, str) and u.strip()]
            elif isinstance(watchers, str):
                # Si es un string, dividir por comas
                clean_data['watchers_usernames'] = [u.strip() for u in watchers.split(',') if u.strip()]

        # Eliminar 'files' si no hay archivos reales
        if 'files' in clean_data and not request_files:
            clean_data.pop('files')

    # Limpiar campos vacíos
    for k in ['status_name', 'priority_name', 'severity_name', 'issue_type_name', 'assigned_to_username',
              'created_by_username']:
        if k in clean_data and clean_data[k] in (None, ''):
            clean_data.pop(k)

    return clean_data


@extend_schema_view(
    list=extend_schema(
        summary="Listar issues",
        description="Devuelve una lista de issues con filtros opcionales ('status', 'priority', etc.) y ordenación.",
        tags=["Issues"],
        responses=IssueSerializer(many=True),
        parameters=[
            OpenApiParameter('status_name', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by status name"),
            OpenApiParameter('priority_name', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by priority name"),
            OpenApiParameter('severity_name', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by severity name"),
            # Nuevos parámetros para filtrar por usuarios
            OpenApiParameter('assigned_to', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Filter by assigned user ID"),
            OpenApiParameter('assigned_to_username', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by assigned username"),
            OpenApiParameter('created_by', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Filter by creator user ID"),
            OpenApiParameter('created_by_username', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by creator username"),
        ],
        examples=[
            OpenApiExample(
                'Respuesta Ejemplo Lista',
                value=[
                    {"id": 1, "title": "Bug login", "status": 2, },
                    {"id": 2, "title": "Añadir tests", "status": 1, }
                ],
                response_only=True
            ),
            OpenApiExample(
                'Filtrar por asignado',
                summary="Filtrar issues por usuario asignado",
                description="Ejemplo de cómo filtrar issues asignados a un usuario específico",
                value="?assigned_to=5&status=1",
                request_only=True
            ),
            OpenApiExample(
                'Filtrar por creador',
                summary="Filtrar issues por creador",
                description="Ejemplo de cómo filtrar issues creados por un usuario específico",
                value="?created_by_username=admin&priority=3",
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Obtener issue por ID",
        description="Recupera los detalles de un issue específico por su ID.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
        ],
        responses=IssueSerializer,
        examples=[
            OpenApiExample(
                'Respuesta Ejemplo Retrieve',
                value={"id": 1, "title": "Bug login", "description": "Error 500 al hacer login", },
                response_only=True
            )
        ]
    ),
    create=extend_schema(
        summary="Crear un nuevo issue",
        description="Crea un nuevo issue. Puedes usar nombres de referencia (status_name, priority_name, etc.) o adjuntar archivos mediante 'files'.",
        tags=["Issues"],
        request=IssueCreateSerializer,
        responses={201: IssueSerializer},
        examples=[
            OpenApiExample(
                name='Ejemplo básico - Bug crítico',
                summary="Crear un bug crítico con asignación",
                description="Ejemplo típico de creación de un bug crítico asignado a un desarrollador",
                value={
                    "subject": "Error 500 al realizar login con Google OAuth",
                    "description": "Los usuarios reportan error 500 cuando intentan autenticarse usando Google OAuth. El error aparece después de autorizar la aplicación en Google y al redirigir de vuelta a nuestro sistema. Logs muestran 'Invalid state parameter' en el callback.",
                    "status_name": "New",
                    "priority_name": "High",
                    "severity_name": "Critical",
                    "issue_type_name": "Bug",
                    "assigned_to_username": "dev_carlos",
                    "watchers_usernames": ["qa_maria", "lead_pedro"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Ejemplo con archivos adjuntos',
                summary="Issue con múltiples archivos",
                description="Crear un issue adjuntando capturas de pantalla y logs",
                value={
                    "subject": "Interfaz rota en pantalla de configuración",
                    "description": "La página de configuración del usuario muestra elementos superpuestos en resoluciones menores a 1024px. Adjunto capturas y CSS compilado para análisis.",
                    "status_name": "Open",
                    "priority_name": "Medium",
                    "severity_name": "Normal",
                    "issue_type_name": "Bug",
                    "assigned_to_username": "frontend_ana",
                    "watchers_usernames": ["designer_luis"],
                    "files": ["screenshot1.png", "screenshot2.png", "compiled.css"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Ejemplo mínimo',
                summary="Creación con campos mínimos requeridos",
                description="Solo con subject y description (usa valores por defecto)",
                value={
                    "subject": "Optimizar consultas de base de datos",
                    "description": "Las consultas en el dashboard principal tardan más de 3 segundos en ejecutarse. Revisar índices y optimizar queries más pesadas."
                },
                request_only=True
            ),
            OpenApiExample(
                name='Ejemplo Feature Request',
                summary="Solicitud de nueva funcionalidad",
                description="Ejemplo de como crear una solicitud de mejora",
                value={
                    "subject": "Implementar notificaciones push",
                    "description": "Los usuarios han solicitado recibir notificaciones push cuando se les asignan nuevos issues o cuando hay actualizaciones en issues que están observando.",
                    "status_name": "Backlog",
                    "priority_name": "Low",
                    "severity_name": "Enhancement",
                    "issue_type_name": "Feature",
                    "watchers_usernames": ["product_manager", "mobile_dev"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Respuesta exitosa',
                summary="Respuesta después de crear issue",
                description="Datos del issue recién creado con ID asignado",
                value={
                    "id": 15,
                    "subject": "Error 500 al realizar login con Google OAuth",
                    "description": "Los usuarios reportan error 500 cuando intentan autenticarse usando Google OAuth...",
                    "status": {"id": 1, "nombre": "New"},
                    "priority": {"id": 3, "nombre": "High"},
                    "severity": {"id": 1, "nombre": "Critical"},
                    "issue_type": {"id": 1, "nombre": "Bug"},
                    "assigned_to": {"id": 5, "username": "dev_carlos", "email": "carlos@empresa.com"},
                    "created_by": {"id": 1, "username": "admin", "email": "admin@empresa.com"},
                    "watchers": [
                        {"id": 8, "username": "qa_maria", "email": "maria@empresa.com"},
                        {"id": 12, "username": "lead_pedro", "email": "pedro@empresa.com"}
                    ],
                    "created_at": "2025-05-24T10:30:00Z",
                    "updated_at": "2025-05-24T10:30:00Z"
                },
                response_only=True
            )
        ]
    ),
    update=extend_schema(
        summary="Actualizar un issue completamente",
        description="Actualiza todos los campos de un issue existente (PUT). Puedes cambiar asignación, estado, añadir watchers y subir nuevos archivos.",
        tags=["Issues"],
        request=IssueUpdateSerializer,
        responses=IssueSerializer,
        examples=[
            OpenApiExample(
                name='Actualización completa',
                summary="Actualizar issue cambiando múltiples campos",
                description="Ejemplo de actualización completa cambiando status, prioridad y asignación",
                value={
                    "subject": "Error 500 al realizar login con Google OAuth - RESUELTO",
                    "description": "Los usuarios reportan error 500 cuando intentan autenticarse usando Google OAuth. \n\nUPDATE: Se identificó que el problema era en la configuración del callback URL. Se ha corregido y desplegado en producción.",
                    "status_name": "Resolved",
                    "priority_name": "High",
                    "severity_name": "Critical",
                    "issue_type_name": "Bug",
                    "assigned_to_username": "dev_carlos",
                    "watchers_usernames": ["qa_maria", "lead_pedro", "devops_juan"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Cambio de asignación',
                summary="Reasignar issue a otro desarrollador",
                description="Cambiar el responsable del issue y añadir contexto",
                value={
                    "subject": "Optimizar consultas de base de datos",
                    "description": "Se requiere revisión completa de las consultas del dashboard. El desarrollador original está en vacaciones, reasignando a especialista en BD.",
                    "status_name": "In Progress",
                    "priority_name": "High",
                    "assigned_to_username": "dba_specialist",
                    "watchers_usernames": ["dev_original", "team_lead"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Actualización con archivos',
                summary="Añadir documentación y archivos",
                description="Actualizar issue añadiendo documentación técnica",
                value={
                    "subject": "Implementar notificaciones push - Documentación técnica",
                    "description": "Funcionalidad de notificaciones push. Se adjunta documentación técnica y mockups para revisión del equipo.",
                    "status_name": "In Review",
                    "priority_name": "Medium",
                    "severity_name": "Enhancement",
                    "issue_type_name": "Feature",
                    "assigned_to_username": "mobile_dev",
                    "watchers_usernames": ["product_manager", "ux_designer"],
                    "files": ["technical_specs.pdf", "mockups.zip", "api_documentation.md"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Respuesta actualización',
                summary="Respuesta después de actualizar",
                description="Issue actualizado con nuevos valores",
                value={
                    "id": 15,
                    "subject": "Error 500 al realizar login con Google OAuth - RESUELTO",
                    "description": "Los usuarios reportan error 500 cuando intentan autenticarse usando Google OAuth...",
                    "status": {"id": 4, "nombre": "Resolved"},
                    "priority": {"id": 3, "nombre": "High"},
                    "assigned_to": {"id": 5, "username": "dev_carlos", "email": "carlos@empresa.com"},
                    "watchers": [
                        {"id": 8, "username": "qa_maria"},
                        {"id": 12, "username": "lead_pedro"},
                        {"id": 20, "username": "devops_juan"}
                    ],
                    "updated_at": "2025-05-24T14:45:00Z"
                },
                response_only=True
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente un issue",
        description="Modifica solo algunos campos específicos del issue (PATCH). Ideal para cambios rápidos como cambiar estado o prioridad.",
        tags=["Issues"],
        request=IssueUpdateSerializer,
        responses=IssueSerializer,
        examples=[
            OpenApiExample(
                name='Cambio rápido de estado',
                summary="Solo cambiar el estado del issue",
                description="Marcar issue como 'In Progress' sin modificar otros campos",
                value={
                    "status_name": "In Progress"
                },
                request_only=True
            ),
            OpenApiExample(
                name='Actualizar prioridad y asignación',
                summary="Cambiar prioridad y asignar desarrollador",
                description="Elevar prioridad y asignar a desarrollador específico",
                value={
                    "priority_name": "Critical",
                    "assigned_to_username": "senior_dev"
                },
                request_only=True
            ),
            OpenApiExample(
                name='Añadir watchers',
                summary="Agregar observadores al issue",
                description="Añadir miembros del equipo para que reciban notificaciones",
                value={
                    "watchers_usernames": ["qa_team", "project_manager", "client_contact"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Actualizar título y descripción',
                summary="Corregir información del issue",
                description="Actualizar título para mayor claridad y añadir detalles",
                value={
                    "subject": "Error 500 en login OAuth - Callback URL incorrecto",
                    "description": "Error identificado: el callback URL configurado en Google OAuth no coincide con el endpoint real. Causa pérdida del parámetro 'state' durante el redirect."
                },
                request_only=True
            ),
            OpenApiExample(
                name='Cerrar issue',
                summary="Marcar issue como completado",
                description="Cambiar estado a resuelto con comentario final",
                value={
                    "status_name": "Closed",
                    "description": "Issue resuelto. Se corrigió la configuración del callback URL en Google Cloud Console. Verificado en producción - login OAuth funciona correctamente."
                },
                request_only=True
            ),
            OpenApiExample(
                name='Adjuntar archivos adicionales',
                summary="Solo añadir nuevos archivos",
                description="Subir archivos adicionales sin modificar otros campos",
                value={
                    "files": ["log_update.txt", "test_results.png"]
                },
                request_only=True
            ),
            OpenApiExample(
                name='Respuesta parcial',
                summary="Respuesta después de actualización parcial",
                description="Issue con campos actualizados",
                value={
                    "id": 15,
                    "subject": "Error 500 en login OAuth - Callback URL incorrecto",
                    "status": {"id": 2, "nombre": "In Progress"},
                    "priority": {"id": 1, "nombre": "Critical"},
                    "assigned_to": {"id": 8, "username": "senior_dev", "email": "senior@empresa.com"},
                    "updated_at": "2025-05-24T16:20:00Z"
                },
                response_only=True
            )
        ]
    ),
    destroy=extend_schema(
        summary="Eliminar un issue",
        description="Elimina un issue por su ID.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del issue a eliminar"
            ),
        ],
        responses={204: None},
    ),
    add_attachment=extend_schema(
        summary="Añadir archivos a un issue",
        description="Adjunta uno o varios archivos a un issue existente.",
        tags=["Issues"],
        request=AttachmentUploadSerializer,
        responses=AttachmentSerializer(many=True),
        examples=[
            OpenApiExample(
                'Ejemplo Request Add Attachment',
                value={"file": ["<file1>", "<file2>"]},
                request_only=True
            )
        ]
    ),
    remove_attachment=extend_schema(
        summary="Eliminar un archivo adjunto",
        description="Elimina un attachment específico de un issue.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
            OpenApiParameter('attachment_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del attachment"),
        ],
        responses={204: None}
    ),
)
class IssueViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
    queryset = Issue.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = IssueFilter
    ordering_fields = [
        'created_at', 'updated_at', 'priority', 'status', 'severity',
        'issue_type', 'created_by', 'assigned_to'
    ]
    ordering = ['-created_at']

    serializer_class = IssueSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return IssueCreateSerializer
        elif self.action in ('update', 'partial_update'):
            return IssueUpdateSerializer
        elif self.action == 'bulk_create':
            return IssueBulkCreateSerializer
        return IssueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'bulk_create':
            return qs.none()
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Normalizar datos usando la función auxiliar
        clean_data = normalize_request_data(request.data, request.FILES)

        # Crear issue con datos limpios
        create_serializer = self.get_serializer(data=clean_data)
        create_serializer.is_valid(raise_exception=True)

        # Guardar issue
        issue = create_serializer.save(created_by=request.user)

        # Devolver respuesta
        response_serializer = IssueSerializer(issue)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Normalizar datos usando la función auxiliar
        clean_data = normalize_request_data(request.data, request.FILES)

        # Actualizar issue
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        update_serializer = self.get_serializer(instance, data=clean_data, partial=partial)
        update_serializer.is_valid(raise_exception=True)

        # Guardar cambios
        issue = update_serializer.save()

        # Manejar archivos si existen
        if request.FILES:
            for f in request.FILES.getlist('files'):
                Attachment.objects.create(issue=issue, file=f)

        # Devolver respuesta
        response_serializer = IssueSerializer(issue)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        # Normalizar datos usando la función auxiliar
        clean_data = normalize_request_data(request.data, request.FILES)

        # Actualizar parcialmente
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        update_serializer = self.get_serializer(instance, data=clean_data, partial=partial)
        update_serializer.is_valid(raise_exception=True)

        # Guardar cambios
        issue = update_serializer.save()

        # Manejar archivos si existen
        if request.FILES:
            for f in request.FILES.getlist('files'):
                Attachment.objects.create(issue=issue, file=f)

        # Devolver respuesta
        response_serializer = IssueSerializer(issue)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Guardar datos antes de eliminar
        response_data = IssueSerializer(instance).data

        self.perform_destroy(instance)

        # Devolver datos del issue eliminado
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Permite crear muchos issues a la vez",
        description="Crea múltiples issues sin aplicar filtros ni paginación.",
        tags=["Issues"],
        request=IssueBulkCreateSerializer,
        responses={201: IssueSerializer(many=True)},
        filters=False,
        examples=[
            OpenApiExample(
                name="Bulk Create Request",
                summary="Ejemplo de petición para crear dos issues",
                description="Se envía una lista de objetos con el campo 'subject'.",
                value={
                    "issues": [
                        {"subject": "Error al guardar perfil"},
                        {"subject": "Mejorar rendimiento API"}
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Bulk Create Response",
                summary="Respuesta tras crear issues",
                description="Se devuelven los datos de los issues recién creados, incluyendo el 'id'.",
                value=[
                    {"id": 10, "subject": "Error al guardar perfil"},
                    {"id": 11, "subject": "Mejorar rendimiento API"}
                ],
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='bulk-create',
        parser_classes=[JSONParser],
        filter_backends=[],
        pagination_class=None,
        serializer_class=IssueBulkResponseSerializer
    )
    def bulk_create(self, request):
        in_serializer = IssueBulkCreateSerializer(data=request.data, context={'request': request})
        in_serializer.is_valid(raise_exception=True)
        created_qs = in_serializer.save()

        out_serializer = IssueSerializer(created_qs, many=True)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Buscar issues por texto",
        description="Devuelve todos los issues cuyo subject o description contienen el término dado.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter(
                name="term",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Texto a buscar en subject o description",
            )
        ],
        responses=IssueSerializer(many=True),
        examples=[
            OpenApiExample(
                name="Búsqueda con resultados",
                summary="Buscar issues que incluyan 'login'",
                description="Devuelve una lista de issues que contienen la palabra 'login' en subject o description.",
                value=[
                    {
                        "id": 1,
                        "subject": "Error de login en app móvil",
                        "description": "Al intentar iniciar sesión desde la app, se lanza un error 500.",
                        "created_at": "2025-04-18T12:34:56Z",
                        "due_date": "2025-04-25",
                        "status": {"id": 2, "nombre": "Abierto"},
                        "priority": {"id": 3, "nombre": "Alta"},
                        "severity": {"id": 1, "nombre": "Crítica"},
                        "issue_type": {"id": 4, "nombre": "Bug"},
                        "assigned_to": {"id": 7, "username": "developer_juan", "email": "juan@example.com"},
                        "created_by": {"id": 1, "username": "admin", "email": "admin@example.com"},
                        "watchers": [
                            {"id": 8, "username": "qa_maria", "email": "maria@example.com"},
                            {"id": 9, "username": "lead_pedro", "email": "pedro@example.com"}
                        ],
                        "attachment": [
                            {"id": 101, "file": "/media/attachments/log-error-20250418.txt"}
                        ],
                        "comments": [
                            {
                                "id": 201,
                                "user": {"id": 8, "username": "qa_maria"},
                                "text": "Este error se produce solo en Android",
                                "created_at": "2025-04-19T09:00:00Z"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "subject": "Login lento en portal web",
                        "description": "El inicio de sesión tarda más de 10 segundos.",
                        "created_at": "2025-04-17T10:00:00Z",
                        "due_date": "2025-04-22",
                        "status": {"id": 2, "nombre": "Abierto"},
                        "priority": {"id": 2, "nombre": "Media"},
                        "severity": {"id": 2, "nombre": "Alta"},
                        "issue_type": {"id": 5, "nombre": "Performance"},
                        "assigned_to": {"id": 10, "username": "backend_luis", "email": "luis@example.com"},
                        "created_by": {"id": 1, "username": "admin", "email": "admin@example.com"},
                        "watchers": [],
                        "attachment": [],
                        "comments": []
                    }
                ],
                response_only=True,
                status_codes=["200"]
            )]
    )
    @action(detail=False, methods=['get'], url_path=r'search/(?P<term>[^/.]+)')
    def search(self, request, term=None):
        qs = self.get_queryset().filter(
            Q(subject__icontains=term) |
            Q(description__icontains=term)
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        if self.action == 'bulk_create':
            return queryset
        return super().filter_queryset(queryset)

    # Agrega estas acciones a tu IssueViewSet existente

    @extend_schema(
        summary="Eliminar watcher de un issue",
        description="Elimina un watcher específico de un issue.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
            OpenApiParameter('watcher_id', OpenApiTypes.INT, OpenApiParameter.PATH,
                             description="ID del usuario watcher"),
        ],
        responses={204: None, 404: {"description": "Issue o watcher no encontrado"}}
    )
    @action(
        detail=True,
        methods=['delete'],
        url_path=r'watchers/(?P<watcher_id>[^/.]+)'
    )
    def remove_watcher(self, request, pk=None, watcher_id=None):
        """Eliminar un watcher específico de un issue"""
        try:
            issue = self.get_object()
            watcher_id = int(watcher_id)

            # Verificar que el watcher existe en el issue
            if not issue.watchers.filter(id=watcher_id).exists():
                return Response(
                    {"detail": "Watcher not found in this issue"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Eliminar el watcher
            issue.watchers.remove(watcher_id)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValueError:
            return Response(
                {"detail": "Invalid watcher ID"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Eliminar attachment de un issue",
        description="Elimina un attachment específico de un issue.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
            OpenApiParameter('attachment_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del attachment"),
        ],
        responses={204: None, 404: {"description": "Issue o attachment no encontrado"}}
    )
    @action(
        detail=True,
        methods=['delete'],
        url_path=r'attachments/(?P<attachment_id>[^/.]+)'
    )
    def remove_attachment(self, request, pk=None, attachment_id=None):
        """Eliminar un attachment específico de un issue"""
        try:
            issue = self.get_object()
            attachment_id = int(attachment_id)

            # Buscar el attachment
            try:
                attachment = Attachment.objects.get(id=attachment_id, issue=issue)
            except Attachment.DoesNotExist:
                return Response(
                    {"detail": "Attachment not found in this issue"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Eliminar el archivo del storage y el registro de la base de datos
            if attachment.file:
                attachment.file.delete(save=False)
            attachment.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValueError:
            return Response(
                {"detail": "Invalid attachment ID"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Remover asignación de un issue",
        description="Elimina la asignación (assigned_to) de un issue, dejándolo sin asignar.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
        ],
        responses={204: None, 404: {"description": "Issue no encontrado"}}
    )
    @action(
        detail=True,
        methods=['delete'],
        url_path='assignment'
    )
    def remove_assignment(self, request, pk=None):
        """Eliminar la asignación (assigned_to) de un issue"""
        try:
            issue = self.get_object()

            if issue.assigned_to is None:
                return Response(
                    {"detail": "Issue is not assigned to anyone"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Remover la asignación
            issue.assigned_to = None
            issue.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Eliminar todos los watchers de un issue",
        description="Elimina todos los watchers de un issue de una vez.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
        ],
        responses={204: None, 404: {"description": "Issue no encontrado"}}
    )
    @action(
        detail=True,
        methods=['delete'],
        url_path='watchers'
    )
    def remove_all_watchers(self, request, pk=None):
        """Eliminar todos los watchers de un issue"""
        try:
            issue = self.get_object()
            issue.watchers.clear()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Eliminar todos los attachments de un issue",
        description="Elimina todos los attachments de un issue de una vez.",
        tags=["Issues"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
        ],
        responses={204: None, 404: {"description": "Issue no encontrado"}}
    )
    @action(
        detail=True,
        methods=['delete'],
        url_path='attachments'
    )
    def remove_all_attachments(self, request, pk=None):
        """Eliminar todos los attachments de un issue"""
        try:
            issue = self.get_object()

            # Eliminar todos los archivos del storage
            for attachment in issue.attachment.all():
                if attachment.file:
                    attachment.file.delete(save=False)

            # Eliminar todos los registros de la base de datos
            issue.attachment.all().delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )