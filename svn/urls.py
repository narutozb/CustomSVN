from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import RepositoryViewSet, CommitViewSet, UserViewSet, receive_svn_data, get_user_token, get_latest_revision

router = DefaultRouter()
router.register(r'repositories', RepositoryViewSet)
router.register(r'commits', CommitViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('receive_svn_data/', receive_svn_data, name='receive_svn_data'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api-get-token/', get_user_token, name='api_get_token'),
    path('repositories/<str:repo_name>/latest_revision/', get_latest_revision, name='get_latest_revision'),
    path('', include(router.urls)),
]
