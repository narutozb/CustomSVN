from django.urls import path
from .views import svn_latest_existed_view

urlpatterns = [

    path('file_changes/list_latest_exit_file_changes_data/', svn_latest_existed_view,
         name='list_latest_exit_file_changes_data')

]
