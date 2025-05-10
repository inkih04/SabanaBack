from rest_framework import mixins,viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User

from django.contrib.auth.models import User
from api.serializers.UserSerializer import ExtendedUserSerializer

from drf_spectacular.utils import (
    extend_schema_view, extend_schema,
    OpenApiParameter, OpenApiTypes, OpenApiExample, OpenApiResponse
)

@extend_schema_view(
    list=extend_schema(
        summary="Obtener usuarios del sistema",
        description="Devuelve una lista de usuarios i los filtra por nombre.",
        tags=['Users'],
        parameters=[
            OpenApiParameter(
                name='username',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtro para buscar usuarios a traves de su nombre de usuario.",
                required=False
            ),
            OpenApiParameter(
                name='bio',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtro para buscar usuarios por su biografía.",
                required=False
            ),
        ],
        responses=ExtendedUserSerializer(many=True),
        examples=[
            OpenApiExample(
                'UserListExample',
                summary="Listado de Usuarios",
                description="Respuesta con todos los Usuarios",
                value=[
                    {
                        "id": 1,
                        "username": "victor",
                        "email": "",
                        "profile_id": 1,
                        "watched_issues_count": 0,
                        "assigned_issues_count": 1,
                        "created_issues_count": 0,
                        "comments_count": 0
                    },
                    {
                        "id": 3,
                        "username": "david",
                        "email": "",
                        "profile_id": 3,
                        "watched_issues_count": 6,
                        "assigned_issues_count": 5,
                        "created_issues_count": 5,
                        "comments_count": 0
                    },
                    {
                        "id": 4,
                        "username": "david5",
                        "email": "",
                        "profile_id": 4,
                        "watched_issues_count": 0,
                        "assigned_issues_count": 0,
                        "created_issues_count": 0,
                        "comments_count": 1
                    },
                ],
                response_only=True,
            ),
            OpenApiExample(
                'UserListFilterResponse',
                summary="Respuesta al filtrar por nombre de usuario",
                description="Ejemplo de respuesta al filtrar por nombre de usuario 'david'.",
                value=[
                    {
                        "id": 3,
                        "username": "david",
                        "email": "",
                        "profile_id": 3,
                        "watched_issues_count": 6,
                        "assigned_issues_count": 5,
                        "created_issues_count": 5,
                        "comments_count": 0
                    },
                    {
                        "id": 4,
                        "username": "david5",
                        "email": "",
                        "profile_id": 4,
                        "watched_issues_count": 0,
                        "assigned_issues_count": 0,
                        "created_issues_count": 0,
                        "comments_count": 1
                    },
                ],
                response_only=True
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Obtener un Usuario a partir de su id",
        description="Recupera los detalles del usuario por su ID.",
        tags=['Users'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del usuario",
                required=True,
            ),
        ],
        responses = {
            200: ExtendedUserSerializer,
            404: OpenApiResponse(
                description="Usuario no encontrado",
                examples=[
                    OpenApiExample(
                        'NotFound',
                        summary="Usuario no encontrado",
                        value={"detail": "No User matches the given query."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                'RetrieveUserExample',
                summary="Obtener un Usuario",
                response_only=True,
                value={
                    "id": 3,
                    "username": "david",
                    "email": "",
                    "profile_id": 3,
                    "watched_issues_count": 6,
                    "assigned_issues_count": 5,
                    "created_issues_count": 5,
                    "comments_count": 0
                },
            ),
        ],
    ),

)
class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = ExtendedUserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('username')
        bio = self.request.query_params.get('bio')
        if name:
            queryset = queryset.filter(username__icontains=name)
        if bio:
            queryset = queryset.filter(profile__biography__icontains=bio)
        return queryset