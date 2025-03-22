from django.urls import path, include
from .views import issue_list, issue_create

urlpatterns = [
    path('', issue_list, name='issue_list'),
    path('new/', issue_create, name='issue_create'),
]
