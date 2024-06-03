from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Repository, Commit, FileChange
from .serializers import RepositorySerializer, CommitSerializer, FileChangeSerializer
from django.db.models import IntegerField, Count
from django.db.models.functions import Cast


class CustomPagination(PageNumberPagination):
    page_size = 200  # 每页显示的记录数，可以在此调整

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,  # 自定义返回值
            'page_count': self.page.paginator.num_pages,  # 自定义返回值
            'current_page': self.page.number,  # 自定义返回值
            'last_page': self.page.paginator.num_pages,  # 自定义返回值
            'results': data,
        })


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
            serializer = CommitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommitSerializer(commits, many=True)
        return Response(serializer.data)


class CommitViewSet(viewsets.ModelViewSet):
    queryset = Commit.objects.annotate(file_changes_count=Count('file_changes')).order_by('-revision')
    serializer_class = CommitSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def file_changes(self, request, pk=None):
        commit = self.get_object()
        file_changes = commit.file_changes.all()
        serializer = FileChangeSerializer(file_changes, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_svn_data(request):
    if request.method == 'POST':
        try:
            data = request.data
            repo_data = data['repository']
            commits_data = data['commits']

            # 检查仓库是否存在
            try:
                repository = Repository.objects.get(name=repo_data['name'], url=repo_data['url'])
            except Repository.DoesNotExist:
                return Response({'status': 'error', 'message': 'Repository does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)

            for commit_data in commits_data:
                commit, created = Commit.objects.get_or_create(
                    repository=repository,
                    revision=commit_data['revision'],
                    defaults={
                        'author': commit_data['author'],
                        'message': commit_data['message'],
                        'date': commit_data['date']
                    }
                )

                if created:
                    for file_change_data in commit_data['file_changes']:
                        FileChange.objects.get_or_create(
                            commit=commit,
                            file_path=file_change_data['file_path'],
                            change_type=file_change_data['change_type']
                        )

            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)


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
            latest_revision = None
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

        file_change_list = [{'file_path': change.file_path, 'change_type': change.change_type, 'id': change.id} for
                            change in
                            result_page]
        return paginator.get_paginated_response(file_change_list)
    except (Repository.DoesNotExist, Commit.DoesNotExist):
        return Response({'status': 'error', 'message': 'Repository or Commit does not exist'},
                        status=status.HTTP_404_NOT_FOUND)


class FileChangeListLatestExistView(APIView):
    def get(self, request, *args, **kwargs):
        '''
        只显示已存在的最新的FileChange
        可以通过仓库名进行过滤
        '''
        repo_name = request.query_params.get('repo_name', None)  # 获取仓库名称参数
        file_paths = FileChange.objects.values_list('file_path', flat=True).distinct()
        data = []
        for file_path in file_paths:
            # 如果提供了仓库名称，就添加一个过滤条件
            if repo_name:
                latest_commit = FileChange.objects.filter(file_path=file_path,
                                                          commit__repository__name=repo_name).order_by(
                    '-commit__revision').first()
            else:
                latest_commit = FileChange.objects.filter(file_path=file_path).order_by('-commit__revision').first()
            if latest_commit and latest_commit.change_type != 'D':
                data.append({
                    'file_path': latest_commit.file_path,
                    'change_type': latest_commit.change_type,
                    'commit': {
                        'revision': latest_commit.commit.revision,
                        'repository': latest_commit.commit.repository.name,
                    }
                })

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(data, request)
        return paginator.get_paginated_response(result_page)
