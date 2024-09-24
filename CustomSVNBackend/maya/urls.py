from django.urls import path


from .views import maya_file_view

urlpatterns = [
    path('maya_file/<int:file_change_id>/', maya_file_view, name='maya_file'),


]
