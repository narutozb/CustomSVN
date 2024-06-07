from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import UserViewSet, CustomAuthToken

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]
