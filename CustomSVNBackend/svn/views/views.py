import os
from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import IntegerField, Count
from django.db.models import OuterRef, Subquery, F
from django.db.models.functions import Cast
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import date as _date
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from svn._serializers.serializer_commit import CommitQuerySerializer
from svn.models import Repository, Commit, FileChange, Branch
from svn.serializers import RepositorySerializer, CommitSerializer, FileChangeSerializer, BranchSerializer
from svn.pagination import CustomPagination


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = Repository.objects.annotate(commits_count=Count('commits'))
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def commits(self, request, pk=None):
        repository = self.get_object()
        commits = repository.commits.all().order_by('-revision')
        page = self.paginate_queryset(commits)
        if page is not None:
            serializer = CommitQuerySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommitQuerySerializer(commits, many=True)
        return Response(serializer.data)


class CommitViewSet(viewsets.ModelViewSet):
    queryset = Commit.objects.annotate(file_changes_count=Count('file_changes')).order_by('-revision')
    serializer_class = CommitQuerySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def file_changes(self, request, pk=None):
        commit = self.get_object()
        file_changes = commit.file_changes.all()
        serializer = FileChangeSerializer(file_changes, many=True)
        return Response(serializer.data)


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['repository__id']


class FileChangeViewSet(viewsets.ModelViewSet):
    queryset = FileChange.objects.all()
    serializer_class = FileChangeSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_revision(request, repo_name):
    print('get_latest_revision function')
    try:
        repository = Repository.objects.get(name=repo_name)
        latest_commit = repository.commits.annotate(
            revision_int=Cast('revision', IntegerField())
        ).order_by('-revision_int').first()
        if latest_commit:
            latest_revision = latest_commit.revision
        else:
            latest_revision = 0
        return Response({'latest_revision': latest_revision}, status=status.HTTP_200_OK)
    except Repository.DoesNotExist:
        return Response({'status': 'error', 'message': 'Repository does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_commits(request, repo_name):
    try:
        repository = Repository.objects.get(name=repo_name)
        commits = Commit.objects.filter(repository=repository).order_by('revision')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(commits, request)

        commit_list = [
            {'revision': commit.revision, 'author': commit.author, 'message': commit.message, 'date': commit.date} for
            commit in result_page]
        return paginator.get_paginated_response(commit_list)
    except Repository.DoesNotExist:
        return Response({'status': 'error', 'message': 'Repository does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_file_changes(request, repo_name, revision, ):
    change_type = request.GET.get('change_type')
    try:
        repository = Repository.objects.get(name=repo_name)
        commit = Commit.objects.get(repository=repository, revision=revision)
        if change_type:
            file_changes = FileChange.objects.filter(commit=commit, change_type=change_type)
        else:
            file_changes = FileChange.objects.filter(commit=commit)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(file_changes, request)

        file_change_list = [{'file_path': change.path, 'change_type': change.action, 'id': change.id} for
                            change in
                            result_page]
        return paginator.get_paginated_response(file_change_list)
    except (Repository.DoesNotExist, Commit.DoesNotExist):
        return Response({'status': 'error', 'message': 'Repository or Commit does not exist'},
                        status=status.HTTP_404_NOT_FOUND)


def svn_latest_existed_view(request):
    repo_name = request.GET.get('repo_name', Repository.objects.all().first().name)  # 获取仓库名称参数

    # 创建一个Subquery，找到每个file_path的最大revision
    latest_revisions = FileChange.objects.filter(file_path=OuterRef('file_path')).order_by('-commit__revision')

    # 使用annotate将Subquery添加到查询集中
    file_changes = FileChange.objects.annotate(
        latest_revision=Subquery(latest_revisions.values('commit__revision')[:1])
    )

    # 过滤查询集，只保留那些revision等于其最大revision的FileChange对象
    file_changes = file_changes.filter(commit__revision=F('latest_revision'))

    # 如果提供了仓库名称，就添加一个过滤条件
    if repo_name:
        file_changes = file_changes.filter(commit__repository__name=repo_name)

    # 过滤掉已删除的文件
    file_changes = file_changes.exclude(change_type='D')

    data = file_changes.values(
        'id',
        'commit',
        'action',
        'path',
        # 'commit__repository__name',
    )

    # 创建一个Paginator实例
    paginator = Paginator(data, 20)  # 每页显示20条数据

    # 获取页码参数
    page_number = request.GET.get('page')

    # 获取当前页的数据
    page_obj = paginator.get_page(page_number)

    # 将当前页的数据和分页的其他信息传递给模板
    return render(
        request, 'svn/svn_latest_existed.html',
        {
            'page_obj': page_obj,
            'repo_name': repo_name
        }
    )


def svn_repository_home(request, repository_name):
    days = request.GET.get('days', 10)
    days = int(days)
    repo = Repository.objects.get(name=repository_name)
    now = timezone.now()
    five_days_ago = now - timedelta(days=days)
    recent_commits = Commit.objects.filter(repository=repo, date__gte=five_days_ago)
    for commit in recent_commits:
        commit.date_str = _date(commit.date, "Y-m-d")  # 将日期转换为字符串
        commit.file_changes_count = commit.file_changes.count()  # 计算FileChange的个数
    return render(
        request, 'svn/home.html',
        {
            'repo': repo,
            'recent_commits': recent_commits,
        }
    )


def svn_commit_details(request, commit_id):
    commit = get_object_or_404(Commit, id=commit_id)
    file_changes = FileChange.objects.filter(commit=commit)
    # 添加文件后缀的变量
    for file_change in file_changes:
        _, file_change.file_extension = os.path.splitext(file_change.path)
    return render(
        request,
        'svn/commit_details.html',
        {
            'commit': commit,
            'file_changes': file_changes
        }
    )
