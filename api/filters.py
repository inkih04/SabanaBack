import django_filters
from django.contrib.auth.models import User
from django.db.models import Q
from issues.models import Issue, Status, Priorities, Severities, Types


class IssueFilter(django_filters.FilterSet):
    status_name = django_filters.CharFilter(field_name='status__nombre', lookup_expr='icontains')
    priority_name = django_filters.CharFilter(field_name='priority__nombre', lookup_expr='icontains')
    severity_name = django_filters.CharFilter(field_name='severity__nombre', lookup_expr='icontains')

    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id')
    created_by = django_filters.NumberFilter(field_name='created_by__id')

    assigned_to_username = django_filters.CharFilter(field_name='assigned_to__username', lookup_expr='iexact')
    created_by_username = django_filters.CharFilter(field_name='created_by__username', lookup_expr='iexact')

    class Meta:
        model = Issue
        fields = [
            'status_name', 'priority_name', 'severity_name',
            'assigned_to', 'created_by',
            'assigned_to_username', 'created_by_username',
        ]