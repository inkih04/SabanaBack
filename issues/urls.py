from django.urls import path, include
from .views import issue_list, issue_create, delete_issue, update_issue_status, issue_detail, issue_bulk_create, login, \
    update_issue_assignee, profile, update_bio, update_issue_description, add_comment_to_issue, update_issue_info_title, \
    issue_info_delete_comment, settings_list, settings_edit, settings_delete, \
    update_avatar, user_directory
from .views import (issue_list, issue_create, delete_issue, update_issue_status, issue_detail, issue_bulk_create, login, \
    update_issue_assignee, profile, update_bio, update_issue_description, add_comment_to_issue, update_issue_info_title,
                    issue_info_delete_comment, info_issue_upload_attachment, issue_info_delete_attachment,
                    issue_info_remove_watcher, issue_info_add_watcher, issue_info_add_multiple_watchers,
                    issue_info_set_due_date,issue_info_remove_due_date)

urlpatterns = [
    path('', issue_list, name='issue_list'),
    path('new/', issue_create, name='issue_create'),
    path('delete/<int:issue_id>/', delete_issue, name='delete_issue'),

    path('update_status/<int:issue_id>/', update_issue_status, name='update_issue_status'),

    path('update_description/<int:issue_id>/', update_issue_description, name='update_issue_description'),

    path('add_comment_to_issue/<int:issue_id>/', add_comment_to_issue, name='add_comment_to_issue'),

    path('update_issue_info_title/<int:issue_id>/', update_issue_info_title, name='update_issue_info_title'),

    path('issue/<int:issue_id>/comment/<int:comment_id>/delete/',issue_info_delete_comment, name='issue_info_delete_comment'),

    path('info_issue_upload_attachment/<int:issue_id>/', info_issue_upload_attachment, name='info_issue_upload_attachment'),

    path('issue/<int:issue_id>/attachment/<int:attachment_id>/delete/',issue_info_delete_attachment, name='issue_info_delete_attachment'),

    path('issue/<int:issue_id>/unwatch',issue_info_remove_watcher, name='issue_info_remove_watcher'),

    path('issue/<int:issue_id>/watch',issue_info_add_watcher, name='issue_info_add_watcher'),

    path('issue_info_add_multiple_watchers/<int:issue_id>/',issue_info_add_multiple_watchers,name='issue_info_add_multiple_watchers'),

    path('issue/<int:issue_id>/issue_info_set_due_date/', issue_info_set_due_date, name='issue_info_set_due_date'),

    path('issue/<int:issue_id>/issue_info_remove_due_date/', issue_info_remove_due_date, name='issue_info_remove_due_date'),

    path('<int:issue_id>/', issue_detail, name='issue_detail'),

    path("issues/bulk_create/", issue_bulk_create, name="issue_bulk_create"),

    path('issues/<int:issue_id>/assign/', update_issue_assignee, name='update_issue_assignee'),


    path('login/', login, name='custom_login'),


    path('settings/', settings_list, name='settings_list'),
    path('settings/<str:model_name>/new/', settings_edit, name='settings_create'),
    path('settings/<str:model_name>/<int:pk>/edit/', settings_edit, name='settings_edit'),
    path('settings/<str:model_name>/<int:pk>/delete/', settings_delete, name='settings_delete'),


    path('profile/', profile, name='profile'),
    path('profile/<str:username>/', profile, name='user_profile'),  # Para el perfil de otro usuario

    path('update_bio/', update_bio, name='update_bio'),

    path('update-avatar/', update_avatar, name='update_avatar'),

    path('users/', user_directory, name='user_directory'),
]
