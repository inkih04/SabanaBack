from django.urls import path, include
from .views import issue_list, issue_create, delete_issue, update_issue_status, issue_detail, issue_bulk_create, login, \
    update_issue_assignee, profile

urlpatterns = [
    path('', issue_list, name='issue_list'),
    path('new/', issue_create, name='issue_create'),
    path('delete/<int:issue_id>/', delete_issue, name='delete_issue'),

    path('update_status/<int:issue_id>/', update_issue_status, name='update_issue_status'),

    path('<int:issue_id>/', issue_detail, name='issue_detail'),

    path("issues/bulk_create/", issue_bulk_create, name="issue_bulk_create"),

    path('issues/<int:issue_id>/assign/', update_issue_assignee, name='update_issue_assignee'),


    path('login/', login, name='custom_login'),

    path('profile/', profile, name='profile'),


]
