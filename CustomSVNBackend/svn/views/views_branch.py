from django_filters import rest_framework as filters

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from django.db.models import Q, Subquery, F, OuterRef
from svn._serializers.serializer_branch import BranchQuerySerializer, BranchQuerySerializerS
from svn._serializers.serializer_commit import CommitQuerySerializer
from svn._serializers.serializer_file_change import FileChangeQuerySerializer
from svn.models import Branch, Commit, FileChange
from svn.pagination import CustomPagination


class BranchFilter(filters.FilterSet):
    name = filters.CharFilter()
    name_contains = filters.CharFilter(field_name='name', lookup_expr='icontains')
    repo_name = filters.CharFilter(field_name='repository__name')
    repo_id = filters.NumberFilter(field_name='repository__id')
    commit_id = filters.NumberFilter(field_name='commits__id')

    class Meta:
        model = Branch
        fields = ["name", 'repo_name', 'repo_id', 'name_contains']


class _FileChangeFilter(filters.FilterSet):
    path = filters.CharFilter(field_name='path', lookup_expr='icontains')
    actions = filters.CharFilter(method='filter_actions', label='Multiple Actions')
    kind = filters.CharFilter(field_name='kind', lookup_expr='icontains')

    class Meta:
        model = FileChange
        fields = [
            'path',
            'actions',
            'kind',
        ]

    def filter_actions(self, queryset, name, value):
        action_list = [action.strip() for action in value.split(',') if action.strip()]
        return queryset.filter(action__in=action_list)

class BranchQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchQuerySerializerS
    pagination_class = CustomPagination
    filterset_class = BranchFilter

    @action(detail=False, methods=['GET'])
    def get_root_tags(self, request):
        '''
        获取所有根标签.
        也就是那些只有一层的标签
        例如：/tags, /branches, /trunk, /test, /test1
        但是不包括那些有多层的标签

        可以根据repo_id来过滤结果,并且支持过滤多个repo_id,例如：
        ?repo_id=1&repo_id=2

        '''

        repo_id_list = request.query_params.getlist('repo_id')

        tags = Branch.objects.filter(
            Q(name__regex=r'^/[^/]+$')
        )

        if repo_id_list:
            tags = tags.filter(repository__id__in=repo_id_list)

        return Response(self.get_serializer(tags, many=True).data)

    @action(detail=True, methods=['GET'])
    def commits(self, request, pk=None):
        '''
        获取指定分支的所有提交记录
        '''
        branch = get_object_or_404(Branch, pk=pk)
        commits = Commit.objects.filter(branch=branch)
        page = self.paginate_queryset(commits)

        if page is not None:
            commits = page

        serializer = CommitQuerySerializer(commits, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def file_changes(self, request, pk=None):
        branch = get_object_or_404(Branch, pk=pk)
        file_changes = FileChange.objects.filter(commit__branch=branch)
        page = self.paginate_queryset(file_changes)

        if page is not None:
            file_changes = page

        serializer = FileChangeQuerySerializer(file_changes, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def latest_file_changes(self, request, pk=None):
        branch = self.get_object()
        latest_file_changes = FileChange.objects.filter(
            commit__branch=branch
        ).annotate(
            latest_commit_revision=Subquery(
                FileChange.objects.filter(
                    commit__branch=branch,
                    path=OuterRef('path')
                ).order_by('-commit__revision').values('commit__revision')[:1]
            )
        ).filter(
            commit__revision=F('latest_commit_revision')
        )
        # 手动应用过滤器
        filterset = _FileChangeFilter(request.GET, queryset=latest_file_changes)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        filtered_latest_file_changes = filterset.qs
        # 应用分页
        page = self.paginate_queryset(filtered_latest_file_changes)
        if page is not None:
            serializer = FileChangeQuerySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = FileChangeQuerySerializer(filtered_latest_file_changes, many=True)
            return Response(serializer.data)




