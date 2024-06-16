from django.urls import path, include
from rest_framework.routers import DefaultRouter

from svn.views.api_views import FileChangeListLatestExistView, GetFileChangeByRevisionView, GetFileChangesByFilePath
from svn.views.views import RepositoryViewSet, CommitViewSet, get_latest_revision, receive_svn_data, list_commits, \
    list_file_changes

router = DefaultRouter()
router.register(r'repositories', RepositoryViewSet)
router.register(r'commits', CommitViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('repositories/<str:repo_name>/latest_revision/', get_latest_revision, name='get_latest_revision'),
    path('receive_svn_data/', receive_svn_data, name='receive_svn_data'),  # 添加receive_svn_data路径
    path('repositories/<str:repo_name>/commits/', list_commits, name='list_commits'),
    path('repositories/<str:repo_name>/commits/<str:revision>/file_changes/', list_file_changes,
         name='list_file_changes'),
    path('repo_name/<str:repo_name>/list_latest_exit_file_changes/', FileChangeListLatestExistView.as_view(),
         name='list_latest_exit_file_changes'),
    path('get_file_change_by_revision/', GetFileChangeByRevisionView.as_view(),
         name='get_file_change_by_revision'),
    path('repo_name/<str:repo_name>/file_changes_by_path/', GetFileChangesByFilePath.as_view(), name='file_changes_by_path')

]
