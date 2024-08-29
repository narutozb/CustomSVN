from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response

from svn._serializers.serializer_file_change import FileChangeQuerySerializer
from svn.models import FileChange
from svn.pagination import CustomPagination


class FileChangeFilter(filters.FilterSet):
    path = filters.CharFilter()
    path_contains = filters.CharFilter(field_name='path', lookup_expr='icontains')
    revision = filters.NumberFilter(field_name='commit__revision')
    revision_from = filters.NumberFilter(field_name='commit__revision', lookup_expr='gte')
    revision_to = filters.NumberFilter(field_name='commit__revision', lookup_expr='lte')
    revisions = filters.CharFilter(method='filter_revisions', label='Multiple Revisions')
    commit_id = filters.NumberFilter(field_name='commit__id')
    repo_name = filters.CharFilter(field_name='commit__repository__name')
    branch_name = filters.CharFilter(field_name='commit__branch__name')
    author = filters.CharFilter(field_name='commit__author')
    date_from = filters.DateTimeFilter(field_name='commit__date', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='commit__date', lookup_expr='lte')
    repo_id = filters.NumberFilter(field_name='commit__repository__id')
    branch_id = filters.NumberFilter(field_name='commit__branch__id')
    actions = filters.CharFilter(method='filter_actions', label='Multiple Actions')
    kind = filters.CharFilter()

    class Meta:
        model = FileChange
        fields = [
            'path',
            'path_contains',
            'revision',
            'revision_from',
            'revision_to',
            'revisions',
            'commit_id',
            'repo_name',
            'branch_name',
            'author',
            'date_from',
            'date_to',
            'repo_id',
            'branch_id',
            'actions',
            'kind',
        ]

    def filter_revisions(self, queryset, name, value):
        revision_list = [int(rev.strip()) for rev in value.split(',') if rev.strip().isdigit()]
        return queryset.filter(commit__revision__in=revision_list)

    def filter_actions(self, queryset, name, value):
        action_list = [action.strip() for action in value.split(',') if action.strip()]
        return queryset.filter(action__in=action_list)

class FileChangeQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FileChange.objects.all()
    serializer_class = FileChangeQuerySerializer
    pagination_class = CustomPagination
    filterset_class = FileChangeFilter
    ordering_fields = ['revision', 'commit__date',]

    def list(self, request, *args, **kwargs):
        '''
        需要指定1个或多个仓库id,否则返回空列表
        '''

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
