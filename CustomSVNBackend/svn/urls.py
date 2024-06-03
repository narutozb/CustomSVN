from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryViewSet, CommitViewSet, get_latest_revision, receive_svn_data, list_commits, \
    list_file_changes, FileChangeListLatestExistView

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
    path('file_changes/list_latest_exit_file_changes/', FileChangeListLatestExistView.as_view(), )

]
