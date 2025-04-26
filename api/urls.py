# api/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    IssueViewSet, StatusViewSet, ProfileViewSet, SeverityViewSet
)

router = DefaultRouter()
router.register(r'issues', IssueViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'severities', SeverityViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
