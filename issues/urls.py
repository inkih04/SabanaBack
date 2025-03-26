from django.urls import path, include
from .views import issue_list, issue_create, delete_issue, update_issue_status

urlpatterns = [
    path('', issue_list, name='issue_list'),
    path('new/', issue_create, name='issue_create'),
    path('delete/<int:issue_id>/', delete_issue, name='delete_issue'),

    path('update_status/<int:issue_id>/', update_issue_status, name='update_issue_status')

]
