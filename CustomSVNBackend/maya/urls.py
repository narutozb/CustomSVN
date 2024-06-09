from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MayaFileViewSet, SceneInfoViewSet, TransformNodeViewSet, ShapeNodeViewSet, list_maya_file_changes, \
    MayaFileView, maya_file_view

urlpatterns = [
    path('maya_file/<int:file_change_id>/', maya_file_view, name='maya_file')

]
