from django.urls import path, include
from rest_framework.routers import DefaultRouter

from svn.views.api_views import FileChangeListLatestExistView, GetFileChangesByFilePath, \
    CommitSearchView, CommitDetailView, CommitsByFilePathView, GetFileChangeDetail
from svn.views.views import RepositoryViewSet, CommitViewSet, get_latest_revision, list_commits, list_file_changes, \
    BranchViewSet, FileChangeViewSet

from svn.views.update_svn import receive_commits
from svn.views.views_commit import CommitQueryViewSet
from svn.views.views_repository import RepositoryQueryViewSet

router = DefaultRouter()
router.register(r'repositories', RepositoryViewSet)
router.register(r'commits', CommitViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'file_changes', FileChangeViewSet)
router.register(r'commits_query', CommitQueryViewSet, basename='Commits-Query')
router.register('repositories_query', RepositoryQueryViewSet, basename='Repositories-Query')

urlpatterns = [
    path('', include(router.urls)),
    path('repositories/<str:repo_name>/latest_revision/', get_latest_revision, name='get_latest_revision'),
    path('receive_commits/', receive_commits, name='receive_svn_data'),  # 接收并且储存commits数据
    path('repositories/<str:repo_name>/commits/', list_commits, name='list_commits'),
    path('repositories/<str:repo_name>/commits/<str:revision>/file_changes/', list_file_changes,
         name='list_file_changes'),
    path('repo_name/<str:repo_name>/list_latest_exit_file_changes/', FileChangeListLatestExistView.as_view(),
         name='list_latest_exit_file_changes'),

    path('repo_name/<str:repo_name>/file_changes_by_path/', GetFileChangesByFilePath.as_view(),
         name='file_changes_by_path'),
    path('_commits/search/', CommitSearchView.as_view(), name='commit-search'),
    path('_commits/commit-details/<int:commit_id>/', CommitDetailView.as_view(), name='commit-details'),
    path('_commits/by-file-path/', CommitsByFilePathView.as_view(), name='commits-by-file-path'),
    path('_file_changes/<int:file_change_id>/', GetFileChangeDetail.as_view(), name='file-change-detail'),

]
