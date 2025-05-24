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
from ..serializers import IssueSerializer, AttachmentSerializer, IssueBulkCreateSerializer, IssueCreateSerializer, IssueUpdateSerializer
from ..serializers.IssueUpdateSerializer import IssueUpdateSerializer
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
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by status id"),
            OpenApiParameter('priority', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by priority id"),
            OpenApiParameter('severity', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by severity id"),
            OpenApiParameter('status_name', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by status name"),
            OpenApiParameter('priority_name', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by priority name"),
            OpenApiParameter('severity_name', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by severity name"),
        ],
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
                value={"id": 1, "title": "Bug login", "description": "Error 500 al hacer login", },
                response_only=True
            )
        ]
    ),
    create=extend_schema(
        summary="Crear un nuevo issue",
        description="Crea un nuevo issue. Se pueden adjuntar archivos usando el campo 'files'.",
        tags=["Issues"],
        request=IssueCreateSerializer,
        responses={201: IssueSerializer},
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
                value={"id": 3, "title": "Bug registro", "status": 1, },
                response_only=True
            )
        ]
    ),
    update=extend_schema(
        summary="Actualizar un issue",
        description="Actualiza campos de un issue existente (parcial o completo)."
                    "Se pueden subir nuevos archivos con 'files'.",
        tags=["Issues"],
        request=IssueUpdateSerializer,
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
    partial_update=extend_schema(
        summary="Actualizar parcialmente un issue",
        description="Modifica solo algunos campos del issue.",
        tags=["Issues"],
        request=IssueUpdateSerializer,
        responses=IssueSerializer,
        examples=[
            OpenApiExample(
                'Ejemplo PATCH',
                value={"title": "Nuevo título"},
                request_only=True
            )
        ]
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

        if isinstance(request.data, QueryDict):
            qd = request.data.copy()
            qd._mutable = True
        else:
            qd = request.data.copy()

        if hasattr(request.data, 'getlist'):
            raw = request.data.getlist('watchers_usernames')
            if raw:
                qd.setlist('watchers_usernames', [u.strip() for u in raw if isinstance(u, str) and u.strip()])
            else:
                qd.pop('watchers_usernames', None)

        if 'files' in qd and not request.FILES:
            qd.pop('files')

        clean_data = {}
        for key, vals in qd.lists():
            if key in ('watchers_usernames', 'watchers_ids', 'files'):
                clean_data[key] = vals
            else:
                clean_data[key] = vals[0] if len(vals) == 1 else vals


        for k in ['status_name', 'priority_name', 'severity_name', 'issue_type_name', 'assigned_to_username']:
            if k in clean_data and clean_data[k] in (None, ''):
                clean_data.pop(k)


        create_serializer = self.get_serializer(data=clean_data)
        create_serializer.is_valid(raise_exception=True)


        issue = create_serializer.save(created_by=request.user)


        response_serializer = IssueSerializer(issue)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            qd = request.data.copy()
            qd._mutable = True
        else:
            qd = request.data.copy()


        if hasattr(request.data, 'getlist'):
            raw = request.data.getlist('watchers_usernames')
            if raw:
                qd.setlist('watchers_usernames', [u.strip() for u in raw if isinstance(u, str) and u.strip()])
            else:
                qd.pop('watchers_usernames', None)


        if 'files' in qd and not request.FILES:
            qd.pop('files')


        clean_data = {}
        for key, vals in qd.lists():
            if key in ('watchers_usernames', 'watchers_ids', 'files'):
                clean_data[key] = vals
            else:
                clean_data[key] = vals[0] if len(vals) == 1 else vals


        for k in ['status_name', 'priority_name', 'severity_name', 'issue_type_name', 'assigned_to_username']:
            if k in clean_data and clean_data[k] in (None, ''):
                clean_data.pop(k)


        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        update_serializer = self.get_serializer(instance, data=clean_data, partial=partial)
        update_serializer.is_valid(raise_exception=True)


        issue = update_serializer.save()
        if request.FILES:
            for f in request.FILES.getlist('files'):
                Attachment.objects.create(issue=issue, file=f)


        response_serializer = IssueSerializer(issue)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            qd = request.data.copy()
            qd._mutable = True
        else:
            # request.data es dict cuando es JSON, copiamos para no modificar original
            qd = request.data.copy()

        if hasattr(request.data, 'getlist'):
            raw = request.data.getlist('watchers_usernames')
            if raw:
                qd['watchers_usernames'] = [u.strip() for u in raw if isinstance(u, str) and u.strip()]
            else:
                qd.pop('watchers_usernames', None)

        if 'files' in qd and not request.FILES:
            qd.pop('files')

        clean_data = {}

        if hasattr(qd, 'lists'):
            items = qd.lists()
        else:
            items = ((k, v if isinstance(v, list) else [v]) for k, v in qd.items())

        for key, vals in items:
            if key in ('watchers_usernames', 'watchers_ids', 'files'):
                clean_data[key] = vals
            else:
                clean_data[key] = vals[0] if len(vals) == 1 else vals

        for k in ['status_name', 'priority_name', 'severity_name', 'issue_type_name', 'assigned_to_username']:
            if k in clean_data and clean_data[k] in (None, ''):
                clean_data.pop(k)

        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        update_serializer = self.get_serializer(instance, data=clean_data, partial=partial)
        update_serializer.is_valid(raise_exception=True)

        issue = update_serializer.save()

        if request.FILES:
            for f in request.FILES.getlist('files'):
                Attachment.objects.create(issue=issue, file=f)

        response_serializer = IssueSerializer(issue)
        return Response(response_serializer.data, status=status.HTTP_200_OK)




    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()


        response_data = IssueSerializer(instance).data

        self.perform_destroy(instance)


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