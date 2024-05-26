from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryViewSet, CommitViewSet

router = DefaultRouter()
router.register(r'repositories', RepositoryViewSet)
router.register(r'commits', CommitViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
