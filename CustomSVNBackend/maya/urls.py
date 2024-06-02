from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MayaFileViewSet, SceneInfoViewSet, TransformNodeViewSet, ShapeNodeViewSet, list_maya_file_changes, \
    MayaFileView

router = DefaultRouter()
router.register(r'mayafiles', MayaFileViewSet)
router.register(r'sceneinfos', SceneInfoViewSet)
router.register(r'transformnodes', TransformNodeViewSet)
router.register(r'shapenodes', ShapeNodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<str:repo_name>/<str:revision>/file_changes/', list_maya_file_changes),
    path('mayafilesview/', MayaFileView.as_view())

]
