from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status as drf_status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)

from issues.models import Status, Issue
from ..serializers import StatusSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Listar statuses",
        description="Devuelve una lista de status con ordenación.",
        tags=['Statuses'],
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Campos por los que ordenar, ej. `-nombre`",
                required=False
            ),
        ],
        responses=StatusSerializer(many=True),
        examples=[
            OpenApiExample(
                'StatusListExample',
                summary="Listado de estados",
                description="Respuesta con todos los estados ordenados por `id`",
                value=[
                    {"id": 1, "nombre": "Open",   "slug": "open",   "color": "#00FF00"},
                    {"id": 2, "nombre": "Closed", "slug": "closed", "color": "#FF0000"},
                ],
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        tags=['Statuses'],
        request=StatusSerializer,
        responses=StatusSerializer,
        summary="Crear un nuevo status",
        description="Crea un nuevo status a partir de un nombre y un color.",
        examples=[
            OpenApiExample(
                'CreateStatusRequest',
                summary="Payload para crear",
                request_only=True,
                value={"nombre": "Pending", "color": "#FFFF00"}
            ),
            OpenApiExample(
                'CreateStatusResponse',
                summary="Respuesta al crear",
                response_only=True,
                value={"id": 3, "nombre": "Pending", "slug": "pending", "color": "#FFFF00"}
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['Statuses'],
        responses=StatusSerializer,
        summary="Obtener un status dado su id",
        description="Devuelve una status dado su id.",
        examples=[
            OpenApiExample(
                'RetrieveStatusExample',
                summary="Obtener un único estado",
                response_only=True,
                value={"id": 1, "nombre": "Open", "slug": "open", "color": "#00FF00"}
            ),
        ],
    ),
    update=extend_schema(
        tags=['Statuses'],
        request=StatusSerializer,
        responses=StatusSerializer,
        summary="Actualizar un status",
        description="Actualiza campos de un status existente.",
        examples=[
            OpenApiExample(
                'UpdateStatusRequest',
                summary="Payload para actualizar",
                request_only=True,
                value={"nombre": "In Progress", "color": "#0000FF"}
            ),
            OpenApiExample(
                'UpdateStatusResponse',
                summary="Respuesta al actualizar",
                response_only=True,
                value={"id": 1, "nombre": "In Progress", "slug": "in-progress", "color": "#0000FF"}
            ),
        ],
    ),
    destroy=extend_schema(
        tags=['Statuses'],
        responses={204: None},
        summary="Eliminar un status",
        description="Elimina un status dado su id, reasignando sus issues a 'New'.",
        examples=[
            OpenApiExample(
                'DeleteStatusExample',
                summary="Eliminar un estado",
                description="Respuesta vacía con código 204",
                response_only=True,
                value=None
            ),
        ],
    ),
)
class StatusViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    filter_backends   = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields   = ['id', 'nombre', 'created_at']
    ordering          = ['id']

    # Listar
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Campos por los que ordenar, ej. `-nombre`",
                required=False
            ),
        ],
        responses=StatusSerializer(many=True)
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Sobrecarga de update por ID
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "New":
            return Response(
                {"detail": "El status 'New' no se puede editar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    # Sobrecarga de destroy por ID: reasigna issues y luego elimina
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "New":
            return Response(
                {"detail": "El status 'New' no se puede eliminar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        # Reasignar todos los issues de este status a "New"
        new_status = get_object_or_404(Status, nombre="New")
        Issue.objects.filter(status=instance).update(status=new_status)
        return super().destroy(request, *args, **kwargs)

    # Obtener por nombre
    @extend_schema(
        summary="Obtener un status por nombre",
        description="Devuelve un status usando su nombre como parámetro.",
        tags=["Statuses"],
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Nombre único del status"
            )
        ],
        responses=StatusSerializer,
        examples=[
            OpenApiExample(
                'RetrieveByNameExample',
                summary="Obtener status por nombre",
                response_only=True,
                value={"id": 1, "nombre": "Open", "slug": "open", "color": "#00FF00"}
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='Get-by-name/(?P<name>[^/.]+)')
    def retrieve_by_name(self, request, name):
        status_obj = get_object_or_404(Status, nombre=name)
        serializer = self.get_serializer(status_obj)
        return Response(serializer.data)

    # Actualizar por nombre
    @extend_schema(
        summary="Actualizar un status por nombre",
        description="Actualiza un status existente identificado por su nombre.",
        tags=["Statuses"],
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Nombre único del status"
            )
        ],
        request=StatusSerializer,
        responses=StatusSerializer,
        examples=[
            OpenApiExample(
                'UpdateByNameRequest',
                summary="Payload para actualizar por nombre",
                request_only=True,
                value={"nombre": "En revisión", "color": "#123456"}
            ),
            OpenApiExample(
                'UpdateByNameResponse',
                summary="Respuesta al actualizar por nombre",
                response_only=True,
                value={"id": 4, "nombre": "En revisión", "slug": "en-revision", "color": "#123456"}
            ),
        ]
    )
    @action(detail=False, methods=['put'], url_path='Put-by-name/(?P<name>[^/.]+)')
    def update_by_name(self, request, name):
        status_obj = get_object_or_404(Status, nombre=name)
        if status_obj.nombre == "New":
            return Response(
                {"detail": "El status 'New' no se puede editar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(status_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # Eliminar por nombre: reasigna issues y luego elimina
    @extend_schema(
        summary="Eliminar un status por nombre",
        description="Elimina un status usando su nombre como parámetro, reasignando sus issues a 'New'.",
        tags=["Statuses"],
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Nombre único del status"
            )
        ],
        responses={204: None},
        examples=[
            OpenApiExample(
                'DeleteByNameExample',
                summary="Eliminar por nombre",
                description="Respuesta vacía con código 204 al eliminar por nombre",
                response_only=True,
                value=None
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='Delete-by-name/(?P<name>[^/.]+)')
    def destroy_by_name(self, request, name):
        status_obj = get_object_or_404(Status, nombre=name)
        if status_obj.nombre == "New":
            return Response(
                {"detail": "El status 'New' no se puede eliminar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        new_status = get_object_or_404(Status, nombre="New")
        Issue.objects.filter(status=status_obj).update(status=new_status)
        status_obj.delete()
        return Response(status=drf_status.HTTP_204_NO_CONTENT)
