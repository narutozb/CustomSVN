from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MayaFileViewSet,  SceneInfoViewSet, TransformNodeViewSet, ShapeNodeViewSet

router = DefaultRouter()
router.register(r'mayafiles', MayaFileViewSet)
router.register(r'sceneinfos', SceneInfoViewSet)
router.register(r'transformnodes', TransformNodeViewSet)
router.register(r'shapenodes', ShapeNodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
