from absl.testing.parameterized import parameters
from django.db.models import Q
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
from ..serializers import IssueSerializer, AttachmentSerializer, IssueBulkCreateSerializer
from ..serializers.issueBulk_serializer import IssueBulkResponseSerializer


class AttachmentUploadSerializer(serializers.Serializer):
    file = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        allow_empty=False,
        help_text="Lista de archivos a adjuntar"
    )


@extend_schema_view(
    list=extend_schema(
        summary="Listar issues",
        description="Devuelve una lista de issues con filtros opcionales ('status', 'priority', etc.) y ordenación.",
        tags=["Issues"],
        responses=IssueSerializer(many=True),
        examples=[
            OpenApiExample(
                'Respuesta Ejemplo Lista',
                value=[
                    {"id": 1, "title": "Bug login", "status": 2, },
                    {"id": 2, "title": "Añadir tests", "status": 1, }
                ],
                response_only=True
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
                value={"id": 1, "title": "Bug login", "description": "Error 500 al hacer login",},
                response_only=True
            )
        ]
    ),
    create=extend_schema(
        summary="Crear un nuevo issue",
        description="Crea un nuevo issue. Se pueden adjuntar archivos usando el campo 'files'.",
        tags=["Issues"],
        request=IssueSerializer,
        responses=IssueSerializer,
        examples=[
            OpenApiExample(
                'Ejemplo Request Create',
                value={
                    "title": "Bug registro",
                    "description": "Al registrarse con email, muestra error.",
                    "priority": 3,
                    "status": 1
                },
                request_only=True
            ),
            OpenApiExample(
                'Respuesta Ejemplo Create',
                value={"id": 3, "title": "Bug registro", "status": 1,},
                response_only=True
            )
        ]
    ),
    update=extend_schema(
        summary="Actualizar un issue",
        description="Actualiza campos de un issue existente (parcial o completo)."
                    "Se pueden subir nuevos archivos con 'files'.",
        tags=["Issues"],
        request=IssueSerializer,
        responses=IssueSerializer,
        examples=[
            OpenApiExample(
                'Ejemplo Request Update',
                value={"title": "Bug login corregido", "status": 2},
                request_only=True
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
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'severity', 'issue_type', 'created_by', 'assigned_to']
    ordering_fields = [
        'created_at', 'updated_at', 'priority', 'status', 'severity',
        'issue_type', 'created_by', 'assigned_to'
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'bulk_create':
            return qs.none()  # o cualquier lógica que impida aplicar filtros
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        issue_data = request.data.copy()
        if 'watchers_usernames' in issue_data and isinstance(issue_data['watchers_usernames'], str):
            issue_data['watchers_usernames'] = [u.strip() for u in issue_data['watchers_usernames'].split(',') if u.strip()]
        serializer = self.get_serializer(data=issue_data)
        serializer.is_valid(raise_exception=True)
        issue = serializer.save()
        for f in request.data.getlist('files', []):
            Attachment.objects.create(issue=issue, file=f)
        return Response(self.get_serializer(issue).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        issue_data = request.data.copy()
        if 'watchers_usernames' in issue_data and isinstance(issue_data['watchers_usernames'], str):
            issue_data['watchers_usernames'] = [u.strip() for u in issue_data['watchers_usernames'].split(',') if u.strip()]
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=issue_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        issue = serializer.save()
        for f in request.data.getlist('files', []):
            Attachment.objects.create(issue=issue, file=f)
        return Response(self.get_serializer(issue).data)

    @action(detail=True, methods=['post'], url_path='attachments')
    def add_attachment(self, request, pk=None):
        issue = self.get_object()
        serializer = AttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachments = [Attachment.objects.create(issue=issue, file=f) for f in serializer.validated_data['file']]
        return Response(AttachmentSerializer(attachments, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='attachments/(?P<attachment_id>[^/.]+)')
    def remove_attachment(self, request, pk=None, attachment_id=None):
        try:
            attachment = Attachment.objects.get(id=attachment_id, issue_id=pk)
            attachment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Attachment.DoesNotExist:
            return Response({"error": "Attachment not found"}, status=status.HTTP_404_NOT_FOUND)




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
        filter_backends=[],      # Anula backends de filtro
        pagination_class=None,
        serializer_class=IssueBulkResponseSerializer
    )
    def bulk_create(self, request):
        # 1) Validamos con el serializer de entrada
        in_serializer = IssueBulkCreateSerializer(data=request.data, context={'request': request})
        in_serializer.is_valid(raise_exception=True)
        created_qs = in_serializer.save()

        # 2) Serializamos la respuesta con el serializer de salida
        out_serializer = self.get_serializer(created_qs, many=True)
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