from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from django.db.models import Max, F, Subquery, OuterRef

from maya.models import TransformNode
from svn._serializers.serializer_commit import CommitQuerySerializerS
from svn._serializers.serializer_file_change import FileChangeQuerySerializer, FileChangeQuerySerializerS
from svn.models import FileChange, Commit
from svn.pagination import CustomPagination
from svn.serializers import FileChangeSerializer


class FileChangeFilter(filters.FilterSet):
    path = filters.CharFilter()
    path_contains = filters.CharFilter(field_name='path', lookup_expr='icontains')
    revision = filters.NumberFilter(field_name='commit__revision')
    revision_from = filters.NumberFilter(field_name='commit__revision', lookup_expr='gte')
    revision_to = filters.NumberFilter(field_name='commit__revision', lookup_expr='lte')
    revisions = filters.CharFilter(method='filter_revisions', label='Multiple Revisions')
    commit_id = filters.NumberFilter(field_name='commit__id')
    commit_ids = filters.CharFilter(method='filter_commits', label='Multiple Commits')
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

    def filter_commits(self, queryset, name, value):
        commit_list = [int(commit.strip()) for commit in value.split(',') if commit.strip().isdigit()]
        return queryset.filter(commit__id__in=commit_list)

    def filter_actions(self, queryset, name, value):
        action_list = [action.strip() for action in value.split(',') if action.strip()]
        return queryset.filter(action__in=action_list)


class FileChangeQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FileChange.objects.all()
    serializer_class = FileChangeQuerySerializer
    pagination_class = CustomPagination
    filterset_class = FileChangeFilter
    ordering_fields = ['revision', 'commit__date', ]

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

    @action(detail=False, methods=['GET'])
    def latest_by_path(self, request):
        """
        获取指定 repository 和 branch 中每个唯一 path 的最新 FileChange 对象
        """
        repo_id = request.query_params.get('repo_id')
        branch_id = request.query_params.get('branch_id')

        if not repo_id or not branch_id:
            return Response({"error": "Both repo_id and branch_id are required."}, status=400)

        # 子查询：获取每个 path 的最新 revision
        latest_revisions = FileChange.objects.filter(
            commit__repository_id=repo_id,
            commit__branch_id=branch_id
        ).values('path').annotate(
            latest_revision=Max('commit__revision')
        )

        # 主查询：获取最新的 FileChange 对象
        queryset = FileChange.objects.filter(
            commit__repository_id=repo_id,
            commit__branch_id=branch_id,
            path__in=Subquery(latest_revisions.values('path')),
            commit__revision__in=Subquery(latest_revisions.values('latest_revision'))
        ).order_by('path', '-commit__revision')

        # 使用 Python 来去重，保留每个 path 的最新记录
        unique_files = {}
        for file_change in queryset:
            if file_change.path not in unique_files:
                unique_files[file_change.path] = file_change

        queryset = list(unique_files.values())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def file_change_details(self, request, pk: None):
        '''
        获取FileChange的详细信息,用于展示在单个FileChange数据页面上
        '''
        queryset = FileChange.objects.get(id=pk)
        serializer = FileChangeQuerySerializer(queryset)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def get_commits_by_self_path(self, request, pk: None):
        obj = FileChange.objects.get(id=pk)
        queryset = Commit.objects.filter(file_changes__path=obj.path).order_by('-date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommitQuerySerializerS(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CommitQuerySerializerS(queryset, many=True)
        return Response(serializer.data)
