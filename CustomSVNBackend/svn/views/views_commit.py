from django.core.paginator import EmptyPage
from django_filters import rest_framework as filters

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from django.db.models import Q, Max
from functools import reduce
from operator import or_

from svn._serializers.serializer_commit import CommitQuerySerializer
from svn._serializers.serializer_file_change import FileChangeQuerySerializer
from svn.models import Commit, FileChange, Repository
from svn.pagination import CustomPagination


class CommitFilter(filters.FilterSet):
    # 现有的过滤器
    repo_name = filters.CharFilter(field_name='repository__name')
    message = filters.CharFilter()
    branch_name = filters.CharFilter(field_name='branch__name')
    revision = filters.NumberFilter()
    branch_id = filters.NumberFilter()

    repo_name_contains = filters.CharFilter(field_name='repository__name', lookup_expr='icontains')
    message_contains = filters.CharFilter(field_name='message', lookup_expr='icontains')
    branch_name_contains = filters.CharFilter(field_name='branch__name', lookup_expr='icontains')

    author = filters.CharFilter(method='filter_authors')
    date_from = filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='date', lookup_expr='lte')

    # 新增的 repository id 过滤器
    repo_id = filters.NumberFilter(field_name='repository__id')

    def filter_authors(self, queryset, name, value):
        # 分割多个作者名称
        authors = [author.strip() for author in value.split(',')]
        return queryset.filter(author__in=authors)

    class Meta:
        model = Commit
        fields = [
            'revision',
            'repo_name',
            'message',
            'branch_name',
            'repo_name_contains',
            'message_contains',
            'branch_name_contains',
            'author',
            'date_from', 'date_to',
            'repo_id',
            'branch_id',
        ]


class CommitQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commit.objects.all()
    serializer_class = CommitQuerySerializer
    pagination_class = CustomPagination
    filterset_class = CommitFilter
    ordering_fields = ['revision', 'date', 'author']

    class CommitQueryViewSet(viewsets.ReadOnlyModelViewSet):
        queryset = Commit.objects.all()
        serializer_class = CommitQuerySerializer
        pagination_class = CustomPagination
        filterset_class = CommitFilter
        ordering_fields = ['revision', 'date', 'author']

    def list(self, request, *args, **kwargs):
        '''
        ?repo_name=repo_name&repo_name_contains=repo_name_contains&repository_id=repository_id
        &branch_name=branch_name&branch_name_contains=branch_name_contains&message=message
        &message_contains=message_contains&author=author1,author2,author3&date_from=date_from&date_to=date_to

        通过参数过滤Commit数据
        可选查询字段: repo_name, repo_name_contains, repository_id, branch_name,
        branch_name_contains, message, message_contains, author (支持多个，用逗号分隔), date_from, date_to
        '''

        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return self.get_empty_paginated_response("No commits found for the specified criteria.")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_empty_paginated_response(self, message):
        # 创建一个自定义的空响应
        paginator = self.pagination_class()
        try:
            page = paginator.paginate_queryset([], self.request, view=self)
        except EmptyPage:
            page = []

        return paginator.get_paginated_response({
            'message': message
        })

    @action(detail=False, methods=['GET'])
    def latest_commit(self, request):
        '''
        通过branch的id查询最新的提交数据
        '''
        branch_id = request.query_params.get('branch_id')

        if not branch_id:
            return Response({"detail": "BranchID parameter is required."}, status=400)

        queryset = Commit.objects.filter(id=branch_id)
        latest_commit = queryset.order_by('-revision').first()

        if not latest_commit:
            return Response({"detail": "No commits found for the specified criteria."}, status=404)

        serializer = self.get_serializer(latest_commit)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def file_changes(self, request, pk=None):
        '''
        ?kind=dir&action=A&action=D&suffix=mb&suffix=ma
        通过参数过滤FileChange数据
        '''
        filter_kind = request.query_params.get('kind')
        filter_actions = request.query_params.getlist('action')
        filter_suffixes = request.query_params.getlist('suffix')

        commit = self.get_object()
        file_changes = FileChange.objects.filter(commit=commit)

        if filter_kind:
            file_changes = file_changes.filter(kind=filter_kind)

        if filter_actions:
            file_changes = file_changes.filter(action__in=filter_actions)

        if filter_suffixes:
            suffix_filters = [Q(path__endswith=f'.{suffix}') for suffix in filter_suffixes]
            file_changes = file_changes.filter(reduce(or_, suffix_filters))

        page = self.paginate_queryset(file_changes)
        if page is not None:
            serializer = FileChangeQuerySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = FileChangeQuerySerializer(file_changes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def authors(self, request):
        '''
        获取所有提交者
        '''
        queryset = self.filter_queryset(self.get_queryset())
        authors = queryset.values('author').annotate(
            max_id=Max('id')
        ).values_list('author', flat=True)
        return Response(authors)
