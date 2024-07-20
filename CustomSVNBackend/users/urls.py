# users/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .views import UserViewSet, LoginView, UserInfoView, LogoutView, TestAPI

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('logout/', views.logout_user, name='logout'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserInfoView.as_view(), name='user_info'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('test/', TestAPI.as_view(), name='test'),

]
