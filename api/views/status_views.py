from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, extend_schema_view

from issues.models import Status
from ..serializers import StatusSerializer


@extend_schema_view(
    list=extend_schema(tags=['Statuses']),
    create=extend_schema(tags=['Statuses']),
    update=extend_schema(tags=['Statuses']),
    retrieve=extend_schema(tags=['Statuses']),
    destroy=extend_schema(tags=['Statuses']),
)
class StatusViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['id', 'nombre', 'created_at']  # ajusta según tus campos
    ordering = ['id']

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
