# api/profile_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User

from issues.models import Profile, Issue, Comment
from api.serializers import IssueSerializer, CommentSerializer
from api.serializers.ProfileSerializer import ProfileSerializer

from drf_spectacular.utils import (
    extend_schema_view, extend_schema,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)


@extend_schema_view(
    retrieve=extend_schema(
        summary="Obtener perfil de usuario",
        description="Recupera los detalles del perfil de un usuario por su ID.",
        tags=["Profile"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description="ID del perfil"),
        ],
        responses=ProfileSerializer,
    ),
    me=extend_schema(
        summary="Obtener perfil del usuario actual",
        description="Devuelve el perfil del usuario actualmente autenticado.",
        tags=["Profile"],
        responses=ProfileSerializer,
    ),
    edit_bio=extend_schema(
        summary="Editar biografía",
        description="Actualiza la biografía del perfil del usuario actual.",
        tags=["Profile"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'biography': {'type': 'string'}
                },
                'required': ['biography']
            }
        },
        responses=ProfileSerializer,
    ),
    edit_profile_picture=extend_schema(
        summary="Editar imagen de perfil",
        description="Actualiza la imagen de perfil del usuario actual. Usa un formulario multipart para subir la imagen.",
        tags=["Profile"],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'avatar': {'type': 'string', 'format': 'binary'}
                },
                'required': ['avatar']
            }
        },
        responses=ProfileSerializer,
    ),
    get_assigned_issues=extend_schema(
        summary="Obtener issues asignados",
        description="Devuelve los issues abiertos asignados al usuario.",
        tags=["Profile"],
        responses=IssueSerializer(many=True),
    ),
    get_watched_issues=extend_schema(
        summary="Obtener issues observados",
        description="Devuelve los issues que el usuario está observando.",
        tags=["Profile"],
        responses=IssueSerializer(many=True),
    ),
    get_user_comments=extend_schema(
        summary="Obtener comentarios del usuario",
        description="Devuelve los comentarios realizados por el usuario.",
        tags=["Profile"],
        responses=CommentSerializer(many=True),
    ),
)
class ProfileViewSet(viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Para acciones de solo lectura (retrieve y acciones personalizadas de consulta),
        # permitir acceso a todos los perfiles
        if self.action in ['retrieve', 'get_assigned_issues', 'get_watched_issues', 'get_user_comments']:
            return Profile.objects.all()

        # Para acciones de escritura, solo permitir acceso al propio perfil
        user = self.request.user
        if user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Devuelve el perfil del usuario actualmente autenticado.
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "No estás autenticado."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Obtener el perfil del usuario actual
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "No se encontró el perfil."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['put'], url_path='edit-bio', parser_classes=[JSONParser])
    def edit_bio(self, request):
        """
        Actualiza la biografía del usuario actual.
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "No estás autenticado."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "No se encontró el perfil."},
                status=status.HTTP_404_NOT_FOUND
            )

        if 'biography' not in request.data:
            return Response(
                {"detail": "El campo 'biography' es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile.biography = request.data['biography']
        profile.save()

        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='edit-picture', parser_classes=[MultiPartParser])
    def edit_profile_picture(self, request):
        """
        Actualiza la imagen de perfil del usuario actual.
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "No estás autenticado."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "No se encontró el perfil."},
                status=status.HTTP_404_NOT_FOUND
            )

        if 'avatar' not in request.FILES:
            return Response(
                {"detail": "El campo 'avatar' es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile.avatar = request.FILES['avatar']
        profile.save()

        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='assigned-issues')
    def get_assigned_issues(self, request, pk=None):
        profile = self.get_object()

        # Obtener issues abiertos asignados al usuario
        # Asumiendo que el estado "Abierto" o "En Progreso" son estados donde el issue está abierto
        # Reemplaza con los IDs reales de tus estados abiertos


        issues = Issue.objects.filter(
            assigned_to=profile.user,
        )

        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='watched-issues')
    def get_watched_issues(self, request, pk=None):
        profile = self.get_object()

        # Obtener issues que el usuario está observando
        issues = profile.user.watched_issues.all()

        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='user-comments')
    def get_user_comments(self, request, pk=None):
        profile = self.get_object()

        # Obtener comentarios del usuario
        comments = Comment.objects.filter(user=profile.user)

        from api.serializers import CommentSerializer
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)