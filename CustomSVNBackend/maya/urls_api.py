from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views.views_maya_file import MayaFileQueryViewSet, MayaFileCommandViewSet
from .api_views.views_maya_file_save_data import ExtendedMayaFileCommandViewSet
from .api_views.views_transform_node import TransformNodeQueryViewSet
from .views import MayaFileViewSet, SceneInfoViewSet, TransformNodeViewSet, ShapeNodeViewSet, list_maya_file_changes, \
    MayaFileView

router = DefaultRouter()
router.register(r'mayafiles', MayaFileViewSet)
router.register(r'sceneinfos', SceneInfoViewSet)
router.register(r'transformnodes', TransformNodeQueryViewSet)
router.register(r'shapenodes', ShapeNodeViewSet)
router.register('mayafile/query', MayaFileQueryViewSet, basename='mayafile-query')
router.register('mayafile/command', MayaFileCommandViewSet, basename='mayafile-command')
router.register('mayafile/save_data', ExtendedMayaFileCommandViewSet, basename='mayafile-save-data')

urlpatterns = [
    path('', include(router.urls)),
    path('<str:repo_name>/<str:revision>/file_changes/', list_maya_file_changes),
    path('mayafilesview/', MayaFileView.as_view()),

]
