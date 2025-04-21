from absl.testing.parameterized import parameters
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
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del issue"),
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
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='bulk-create',
        parser_classes=[JSONParser],
        filter_backends=[],      # Anula backends de filtro
        pagination_class=None,
    )
    def bulk_create(self, request):
        serializer = IssueBulkCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        created_qs = serializer.save()
        return Response(IssueSerializer(created_qs, many=True).data, status=status.HTTP_201_CREATED)

    def filter_queryset(self, queryset):
        if self.action == 'bulk_create':
            return queryset
        return super().filter_queryset(queryset)