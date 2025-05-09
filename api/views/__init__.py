from .issue_views import IssueViewSet
from .status_views import StatusViewSet
from .profile_views import ProfileViewSet
from .severities_view import SeverityViewSet
from .comments_views import CommentViewSet
from .types_view import TypesViewSet
from .priorities_view import PrioritiesViewSet

__all__ = [
    'IssueViewSet',
    'StatusViewSet',
    'ProfileViewSet',
    'SeverityViewSet',
    'CommentViewSet',
    'TypesViewSet',
    'PrioritiesViewSet'
]