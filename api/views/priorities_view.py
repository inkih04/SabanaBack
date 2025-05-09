from django.db import IntegrityError
from rest_framework import viewsets, filters, status
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as drf_status
from django.shortcuts import get_object_or_404
from issues.models import Priorities
from ..serializers import PrioritiesSerializer



@extend_schema_view(
    list=extend_schema(
        summary="Listar prioridades",
        description="Devuelve una lista de prioridades i filtra por nombres similares al parametro name.",
        tags=['Priorities'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtro para que solo aparezcan las prioridades que contengan 'name' en su nombre, és insensible a mayúsculas/minúsculas.",
                required=False
            ),
        ],
        responses=PrioritiesSerializer(many=True),
        examples=[
            OpenApiExample(
                'TypeListExample',
                summary="Listado de prioridades",
                description="Respuesta con todas las prioridades",
                value=[
                    {"id": 1,"nombre": "Urgent", "color": "#FF0000"},
                    {"id": 2,"nombre": "High", "color": "#FFA500" },
                    {"id": 3,"nombre": "Medium","color": "#bb5816"},
                    {"id": 4,"nombre": "Low", "color": "#00FF00"}
                ],
                response_only=True,
            ),
            OpenApiExample(
                'TypeListFilterResponse',
                summary="Respuesta al filtrar por nombre",
                description="Ejemplo de respuesta al filtrar por nombre 'Low'.",
                value=[
                    {"id": 4,"nombre": "Low", "color": "#00FF00"}
                ],
                response_only=True
            ),
        ],
    ),
    create=extend_schema(
        summary="Crea una nueva prioridad",
        description="Crea una nueva prioridad con los parametros recibidos.",
        tags=['Priorities'],
        request=PrioritiesSerializer,
        responses={
            201: PrioritiesSerializer,
            400: OpenApiExample(
                'BadRequest',
                summary="Parámetros inválidos",
                value={"nombre": ["This field is required."]},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                'CreateTypeRequest',
                summary="Body para crear",
                request_only=True,
                value={"nombre": "Low", "color": "#00FF00"}
            ),
            OpenApiExample(
                'CreateTypeResponse',
                summary="Respuesta al crear",
                response_only=True,
                value={"id": 4,"nombre": "Low", "color": "#00FF00"}
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Obtener una prioridad dado su id",
        description="Devuelve una prioridad dado su id.",
        tags=['Priorities'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID de la prioridad a obtener'
            ),
        ],
        responses={
            200: PrioritiesSerializer,
            404: OpenApiExample(
                'NotFound',
                summary="Prioridad no encontrado",
                value={"detail": "No Priorities matches the given query."},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                'RetrieveTypeExample',
                summary="Obtener una prioridad",
                response_only=True,
                value={"id": 4,"nombre": "Low", "color": "#00FF00"}
            ),
        ],
    ),
    update=extend_schema(
        summary="Actualizar una prioridad",
        description="Actualiza campos de una prioridad existente.",
        tags=['Priorities'],
        request=PrioritiesSerializer,
        responses={
            200: PrioritiesSerializer,
            400: OpenApiExample(
                'BadRequest',
                summary="Parámetros inválidos",
                value={ "nombre": ["This field is required." ]},
                response_only=True,
            ),
            404: OpenApiExample(
                'NotFound',
                summary="No encontrado",
                value={"detail": "No Priorities matches the given query."},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                'UpdateTypeRequest',
                summary="Body para actualizar",
                request_only=True,
                value={"nombre": "Low", "color": "#00FF00"}
            ),
            OpenApiExample(
                'UpdateTypeResponse',
                summary="Respuesta al actualizar",
                response_only=True,
                value={"id": 4,"nombre": "Low", "color": "#00FF00"}
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Eliminar una prioridad",
        description="Elimina una prioridad dado su id.",
        tags=['Priorities'],
        responses={
            204: None,
            404: OpenApiExample(
                'NotFound',
                summary="No encontrado",
                value={"detail": "No Priorities matches the given query."},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                'DeleteTypeExample',
                summary="Eliminar una prioridad",
                description="Respuesta vacía con código 204",
                response_only=True,
                value=None
            ),
        ],
    ),
)
class PrioritiesViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Priorities.objects.all()
    serializer_class = PrioritiesSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(nombre__icontains=name)
        return queryset