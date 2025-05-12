from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status as drf_status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)

from issues.models import Severities, Issue
from ..serializers import SeveritiesSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Listar severidades",
        description="Devuelve una lista de severidades con ordenación.",
        tags=['Severities'],
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Campos por los que ordenar, ej. `-nombre`",
                required=False
            ),
        ],
        responses=SeveritiesSerializer(many=True),
        examples=[
            OpenApiExample(
                'SeverityListExample',
                summary="Listado de severidades",
                description="Respuesta con todas las severidades ordenadas por `id`",
                value=[
                    {"id": 1, "nombre": "Critical", "slug": "critical", "color": "#FF0000"},
                    {"id": 2, "nombre": "High",     "slug": "high",     "color": "#FFA500"},
                    {"id": 3, "nombre": "Medium",   "slug": "medium",   "color": "#FFFF00"},
                    {"id": 4, "nombre": "Low",      "slug": "low",      "color": "#00FF00"},
                ],
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        tags=['Severities'],
        request=SeveritiesSerializer,
        responses=SeveritiesSerializer,
        summary="Crear una nueva severidad",
        description="Crea una nueva severidad a partir de un nombre y un color.",
        examples=[
            OpenApiExample(
                'CreateSeverityRequest',
                summary="Payload para crear",
                request_only=True,
                value={"nombre": "Blocker", "color": "#8B0000"}
            ),
            OpenApiExample(
                'CreateSeverityResponse',
                summary="Respuesta al crear",
                response_only=True,
                value={"id": 5, "nombre": "Blocker", "slug": "blocker", "color": "#8B0000"}
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['Severities'],
        responses=SeveritiesSerializer,
        summary="Obtener una severidad dado su id",
        description="Devuelve una severidad dado su id.",
        examples=[
            OpenApiExample(
                'RetrieveSeverityExample',
                summary="Obtener una única severidad",
                response_only=True,
                value={"id": 1, "nombre": "Critical", "slug": "critical", "color": "#FF0000"}
            ),
        ],
    ),
    update=extend_schema(
        tags=['Severities'],
        request=SeveritiesSerializer,
        responses=SeveritiesSerializer,
        summary="Actualizar una severidad",
        description="Actualiza campos de una severidad existente.",
        examples=[
            OpenApiExample(
                'UpdateSeverityRequest',
                summary="Payload para actualizar",
                request_only=True,
                value={"nombre": "Major", "color": "#FF4500"}
            ),
            OpenApiExample(
                'UpdateSeverityResponse',
                summary="Respuesta al actualizar",
                response_only=True,
                value={"id": 2, "nombre": "Major", "slug": "major", "color": "#FF4500"}
            ),
        ],
    ),
    destroy=extend_schema(
        tags=['Severities'],
        responses={204: None},
        summary="Eliminar una severidad",
        description="Elimina una severidad dado su id, reasignando sus issues a 'Normal'.",
        examples=[
            OpenApiExample(
                'DeleteSeverityExample',
                summary="Eliminar una severidad",
                description="Respuesta vacía con código 204",
                response_only=True,
                value=None
            ),
        ],
    ),
)
class SeverityViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Severities.objects.all()
    serializer_class = SeveritiesSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['id', 'nombre', 'created_at']
    ordering = ['id']

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
        responses=SeveritiesSerializer(many=True)
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Sobrecarga de update por ID
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "Normal":
            return Response(
                {"detail": "La severidad 'Normal' no se puede editar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    # Sobrecarga de destroy por ID: reasigna issues y luego elimina
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "Normal":
            return Response(
                {"detail": "La severidad 'Normal' no se puede eliminar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        normal = get_object_or_404(Severities, nombre="Normal")
        Issue.objects.filter(severity=instance).update(severity=normal)
        return super().destroy(request, *args, **kwargs)

    # Obtener por nombre
    @extend_schema(
        summary="Obtener una severidad por nombre",
        description="Devuelve una severidad usando su nombre como parámetro.",
        tags=["Severities"],
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Nombre único de la severidad"
            )
        ],
        responses=SeveritiesSerializer,
        examples=[
            OpenApiExample(
                'RetrieveByNameExample',
                summary="Obtener severidad por nombre",
                response_only=True,
                value={"id": 1, "nombre": "Critical", "slug": "critical", "color": "#FF0000"}
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='Get-by-name/(?P<name>[^/.]+)')
    def retrieve_by_name(self, request, name):
        severity_obj = get_object_or_404(Severities, nombre=name)
        serializer = self.get_serializer(severity_obj)
        return Response(serializer.data)

    # Actualizar por nombre
    @extend_schema(
        summary="Actualizar una severidad por nombre",
        description="Actualiza una severidad existente identificada por su nombre.",
        tags=["Severities"],
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Nombre único de la severidad"
            )
        ],
        request=SeveritiesSerializer,
        responses=SeveritiesSerializer,
        examples=[
            OpenApiExample(
                'UpdateByNameRequest',
                summary="Payload para actualizar por nombre",
                request_only=True,
                value={"nombre": "Highest", "color": "#8B0000"}
            ),
            OpenApiExample(
                'UpdateByNameResponse',
                summary="Respuesta al actualizar por nombre",
                response_only=True,
                value={"id": 1, "nombre": "Highest", "slug": "highest", "color": "#8B0000"}
            ),
        ]
    )
    @action(detail=False, methods=['put'], url_path='Put-by-name/(?P<name>[^/.]+)')
    def update_by_name(self, request, name):
        severity_obj = get_object_or_404(Severities, nombre=name)
        if severity_obj.nombre == "Normal":
            return Response(
                {"detail": "La severidad 'Normal' no se puede editar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(severity_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # Eliminar por nombre: reasigna issues y luego elimina
    @extend_schema(
        summary="Eliminar una severidad por nombre",
        description="Elimina una severidad usando su nombre como parámetro, reasignando sus issues a 'Normal'.",
        tags=["Severities"],
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Nombre único de la severidad"
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
        severity_obj = get_object_or_404(Severities, nombre=name)
        if severity_obj.nombre == "Normal":
            return Response(
                {"detail": "La severidad 'Normal' no se puede eliminar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        normal = get_object_or_404(Severities, nombre="Normal")
        Issue.objects.filter(severity=severity_obj).update(severity=normal)
        severity_obj.delete()
        return Response(status=drf_status.HTTP_204_NO_CONTENT)
