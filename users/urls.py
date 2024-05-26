from django.urls import path
from .views import CustomAuthToken, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
]
