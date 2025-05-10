from django.contrib.auth.models import User
from rest_framework import serializers

from issues.models import Status, Priorities, Types, Severities, Issue, Attachment, Comment, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ExtendedUserSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(source='profile.id', read_only=True)
    watched_issues_count = serializers.SerializerMethodField()
    assigned_issues_count = serializers.SerializerMethodField()
    created_issues_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile_id',
            'watched_issues_count', 'assigned_issues_count',
            'created_issues_count', 'comments_count'
        ]

    def get_watched_issues_count(self, obj) -> int:
        return obj.watched_issues.count()

    def get_assigned_issues_count(self, obj) -> int:
        return Issue.objects.filter(assigned_to=obj).count()

    def get_created_issues_count(self, obj) -> int:
        return obj.created_issues.count()

    def get_comments_count(self, obj) -> int:
        return obj.comments.count()