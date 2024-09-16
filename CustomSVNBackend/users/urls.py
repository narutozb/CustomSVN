# users/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserInfoView, LogoutView, CustomTokenObtainPairView, CustomTokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserInfoView.as_view(), name='user_info'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
