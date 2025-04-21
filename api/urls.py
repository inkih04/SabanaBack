# api/urls.py
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
