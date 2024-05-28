from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryViewSet, CommitViewSet, get_latest_revision, receive_svn_data

router = DefaultRouter()
router.register(r'repositories', RepositoryViewSet)
router.register(r'commits', CommitViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('repositories/<str:repo_name>/latest_revision/', get_latest_revision, name='get_latest_revision'),
    path('receive_svn_data/', receive_svn_data, name='receive_svn_data'),  # 添加receive_svn_data路径

]
