from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status as drf_status
from rest_framework.response import Response
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
        description="Devuelve una lista de statuses con filtrado por nombre.",
        tags=['Statuses'],
        parameters=[
            OpenApiParameter(
                name='nombre',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtra los statuses cuyo nombre contenga el valor dado",
                required=False
            ),
        ],
        responses=StatusSerializer(many=True),
        examples=[
            OpenApiExample(
                'StatusListExample',
                summary="Listado de estados",
                description="Respuesta con todos los estados",
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
        description="Devuelve un status dado su id.",
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

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nombre']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='nombre',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtra los statuses cuyo nombre contenga el valor dado",
                required=False
            ),
        ],
        responses=StatusSerializer(many=True)
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "New":
            return Response(
                {"detail": "El status 'New' no se puede editar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "New":
            return Response(
                {"detail": "El status 'New' no se puede eliminar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        new_status = get_object_or_404(Status, nombre="New")
        Issue.objects.filter(status=instance).update(status=new_status)
        return super().destroy(request, *args, **kwargs)
