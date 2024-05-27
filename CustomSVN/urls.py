"""
URL configuration for CustomSVN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from maya.views import MayaFileViewSet
from users.views import UserViewSet, CustomAuthToken
from svn.views import RepositoryViewSet, CommitViewSet, receive_svn_data

# 定义默认路由器
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'repositories', RepositoryViewSet)
router.register(r'commits', CommitViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # 合并的路由配置
    path('api/api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),  # 添加api-token-auth路径
    path('api/receive_svn_data/', receive_svn_data, name='receive_svn_data'),  # 添加receive_svn_data路径
    path('api/maya/', include('maya.urls'))
]
