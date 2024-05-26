from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import RepositoryViewSet, CommitViewSet,  receive_svn_data,  get_latest_revision

router = DefaultRouter()
router.register(r'repositories', RepositoryViewSet)
router.register(r'commits', CommitViewSet)

urlpatterns = [
    path('receive_svn_data/', receive_svn_data, name='receive_svn_data'),
    path('repositories/<str:repo_name>/latest_revision/', get_latest_revision, name='get_latest_revision'),
    path('', include(router.urls)),
]
