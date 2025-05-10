from django.db import IntegrityError
from rest_framework import viewsets, filters, status
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes, OpenApiExample, OpenApiResponse
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as drf_status
from django.shortcuts import get_object_or_404
from issues.models import Types
from ..serializers import TypesSerializer



@extend_schema_view(
    list=extend_schema(
        summary="Listar tipos",
        description="Devuelve una lista de tipos i filtra por nombres similares al parametro name.",
        tags=['Types'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtro para que solo aparezcan los tipos que contengan 'name' en su nombre, és insensible a mayúsculas/minúsculas.",
                required=False
            ),
        ],
        responses=TypesSerializer(many=True),
        examples=[
            OpenApiExample(
                'TypeListExample',
                summary="Listado de tipos",
                description="Respuesta con todos los tipos",
                value=[
                    {"id": 3,"nombre": "Improvement","color": "#3357FF"},
                    {"id": 5,"nombre": "Question","color": "#1eff00"},
                    {"id": 7,"nombre": "Bug","color": "#FF0000"},
                ],
                response_only=True,
            ),
            OpenApiExample(
                'TypeListFilterResponse',
                summary="Respuesta al filtrar por nombre",
                description="Ejemplo de respuesta al filtrar por nombre 'Bug'.",
                value=[
                    {"id": 7, "nombre": "Bug", "color": "#FF0000"}
                ],
                response_only=True
            ),
        ],
    ),
    create=extend_schema(
        summary="Crea un nuevo tipo",
        description="Crea un nuevo tipo con los parametros recibidos.",
        tags=['Types'],
        request=TypesSerializer,
        responses = {
            201: TypesSerializer,
            400: OpenApiResponse(
                description="Parámetros inválidos",
                examples=[
                    OpenApiExample(
                        'BadRequest',
                        summary="Parámetros inválidos",
                        value={"nombre": ["This field is required."]},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                'CreateTypeRequest',
                summary="Body para crear",
                request_only=True,
                value={"nombre": "Bug", "color": "#FF0000"}
            ),
            OpenApiExample(
                'CreateTypeResponse',
                summary="Respuesta al crear",
                response_only=True,
                value={"id": 7, "nombre": "Bug", "color": "#FF0000"}
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Obtener un tipo dado su id",
        description="Devuelve un tipo dado su id.",
        tags=['Types'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID del tipo a obtener'
            ),
        ],
        responses = {
            200: TypesSerializer,
            404: OpenApiResponse(
                description="Tipo no encontrado",
                examples=[
                    OpenApiExample(
                        'NotFound',
                        summary="Tipo no encontrado",
                        value={"detail": "No Types matches the given query."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                'RetrieveTypeExample',
                summary="Obtener un tipo",
                response_only=True,
                value={"id": 7, "nombre": "Bug", "color": "#FF0000"}
            ),
        ],
    ),
    update=extend_schema(
        summary="Actualizar un tipo",
        description="Actualiza campos de un tipo existente.",
        tags=['Types'],
        request=TypesSerializer,
        responses = {
            200: TypesSerializer,
            400: OpenApiResponse(
                description="Parámetros inválidos",
                examples=[
                    OpenApiExample(
                        'BadRequest',
                        summary="Parámetros inválidos",
                        value={"nombre": ["This field is required."]},
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="No encontrado",
                examples=[
                    OpenApiExample(
                        'NotFound',
                        summary="No encontrado",
                        value={"detail": "No Types matches the given query."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                'UpdateTypeRequest',
                summary="Body para actualizar",
                request_only=True,
                value={"nombre": "Bug", "color": "#FF0000"}
            ),
            OpenApiExample(
                'UpdateTypeResponse',
                summary="Respuesta al actualizar",
                response_only=True,
                value={"id": 7, "nombre": "Bug", "color": "#FF0000"}
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Eliminar un tipo",
        description="Elimina un tipo dado su id.",
        tags=['Types'],
        responses={
            204: OpenApiResponse(description="Eliminado correctamente"),
            404: OpenApiResponse(
                description="No encontrado",
                examples=[
                    OpenApiExample(
                        'NotFound',
                        summary="No encontrado",
                        value={"detail": "No Types matches the given query."},
                        response_only=True,
                        status_codes=['404'],
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                'DeleteTypeExample',
                summary="Eliminar un tipo",
                description="Respuesta vacía con código 204",
                response_only=True,
                value=None
            ),
        ],
    ),
)
class TypesViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Types.objects.all()
    serializer_class = TypesSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(nombre__icontains=name)
        return queryset