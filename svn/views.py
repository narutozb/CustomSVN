from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import Repository, Commit, FileChange
from .serializers import RepositorySerializer, CommitSerializer, FileChangeSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models import F, IntegerField, Count
from django.db.models.functions import Cast


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def commits(self, request, pk=None):
        repository = self.get_object()
        commits = repository.commits.all()
        page = self.paginate_queryset(commits)
        if page is not None:
            serializer = CommitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommitSerializer(commits, many=True)
        return Response(serializer.data)


class CommitViewSet(viewsets.ModelViewSet):
    queryset = Commit.objects.all()
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

            # Check if repository exists
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [AllowAny, ]
        else:
            self.permission_classes = [IsAuthenticated, ]
        return super(UserViewSet, self).get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_token(request):
    user = request.user
    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_200_OK)
