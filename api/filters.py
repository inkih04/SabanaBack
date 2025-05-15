import django_filters
from issues.models import Issue

class IssueFilter(django_filters.FilterSet):
    status_name   = django_filters.CharFilter(field_name='status__nombre', lookup_expr='exact')
    priority_name = django_filters.CharFilter(field_name='priority__nombre', lookup_expr='exact')
    severity_name = django_filters.CharFilter(field_name='severity__nombre', lookup_expr='exact')

    class Meta:
        model = Issue
        fields = [
            'status',
            'priority',
            'severity',
            'status_name',
            'priority_name',
            'severity_name',
        ]
