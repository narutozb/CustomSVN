from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MayaFileViewSet

router = DefaultRouter()
router.register(r'mayafiles', MayaFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
