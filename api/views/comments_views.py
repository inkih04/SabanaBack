from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from issues.models import Comment, Issue
from api.serializers import CommentSerializer

from drf_spectacular.utils import (
    extend_schema_view, extend_schema,
    OpenApiParameter, OpenApiTypes
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar comentarios",
        description="Recupera la lista de todos los comentarios. Se puede filtrar por issue o por usuario.",
        tags=["Comments"],
        parameters=[
            OpenApiParameter('issue', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Filtrar por ID de issue"),
            OpenApiParameter('user', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Filtrar por ID de usuario"),
        ],
        responses=CommentSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Obtener comentario",
        description="Recupera los detalles de un comentario específico por su ID.",
        tags=["Comments"],
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH,
                             description="ID del comentario"),
        ],
        responses=CommentSerializer,
    ),
    create=extend_schema(
        summary="Crear comentario",
        description="Crea un nuevo comentario en un issue.",
        tags=["Comments"],
        request=CommentSerializer,
        responses={201: CommentSerializer},
    ),
    update=extend_schema(
        summary="Actualizar comentario completo",
        description="Actualiza completamente un comentario existente.",
        tags=["Comments"],
        request=CommentSerializer,
        responses=CommentSerializer,
    ),
    partial_update=extend_schema(
        summary="Actualizar comentario parcialmente",
        description="Actualiza parcialmente un comentario existente.",
        tags=["Comments"],
        request=CommentSerializer,
        responses=CommentSerializer,
    ),
    destroy=extend_schema(
        summary="Eliminar comentario",
        description="Elimina un comentario existente.",
        tags=["Comments"],
        responses={204: None},
    ),
    user_comments=extend_schema(
        summary="Comentarios del usuario actual",
        description="Devuelve todos los comentarios realizados por el usuario autenticado.",
        tags=["Comments"],
        responses=CommentSerializer(many=True),
    ),
    issue_comments=extend_schema(
        summary="Comentarios de un issue",
        description="Devuelve todos los comentarios de un issue específico.",
        tags=["Comments"],
        parameters=[
            OpenApiParameter('issue_id', OpenApiTypes.INT, OpenApiParameter.PATH,
                             description="ID del issue"),
        ],
        responses=CommentSerializer(many=True),
    ),
    latest_comments=extend_schema(
        summary="Comentarios recientes",
        description="Devuelve los comentarios más recientes.",
        tags=["Comments"],
        parameters=[
            OpenApiParameter('limit', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Número máximo de comentarios a devolver (predeterminado: 10)"),
        ],
        responses=CommentSerializer(many=True),
    ),
)
class CommentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Comment.objects.all().order_by('-published_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Comment.objects.all().order_by('-published_at')


        issue_id = self.request.query_params.get('issue', None)
        if issue_id is not None:
            queryset = queryset.filter(issue__id=issue_id)


        user_id = self.request.query_params.get('user', None)
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)

        return queryset

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):

        comment = self.get_object()
        if comment.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para editar este comentario."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):

        comment = self.get_object()
        if comment.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar este comentario."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my-comments')
    def user_comments(self, request):

        comments = Comment.objects.filter(user=request.user).order_by('-published_at')


        count = comments.count()

        serializer = self.get_serializer(comments, many=True)
        return Response({
            'count': count,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='issue/(?P<issue_id>[^/.]+)')
    def issue_comments(self, request, issue_id=None):

        issue = get_object_or_404(Issue, pk=issue_id)
        comments = Comment.objects.filter(issue=issue).order_by('-published_at')


        count = comments.count()

        serializer = self.get_serializer(comments, many=True)
        return Response({
            'count': count,
            'results': serializer.data,
            'issue_subject': issue.subject  # Añadir información del issue
        })

    @action(detail=False, methods=['get'], url_path='latest')
    def latest_comments(self, request):

        limit = int(request.query_params.get('limit', 10))
        comments = Comment.objects.all().order_by('-published_at')[:limit]
        serializer = self.get_serializer(comments, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })