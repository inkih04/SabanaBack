# api/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    IssueViewSet, StatusViewSet, ProfileViewSet, SeverityViewSet, CommentViewSet
)

router = DefaultRouter()
router.register(r'issues', IssueViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'severities', SeverityViewSet)

router.register(r'comments', CommentViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
