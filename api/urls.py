# api/urls.py
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    IssueViewSet, StatusViewSet
)

router = DefaultRouter()
router.register(r'issues', IssueViewSet)
router.register(r'statuses', StatusViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
