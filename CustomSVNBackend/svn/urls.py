from django.urls import path
from .views import svn_latest_existed_view, svn_repository_home, svn_commit_details

urlpatterns = [

    path('file_changes/list_latest_exit_file_changes_data/', svn_latest_existed_view,
         name='list_latest_exit_file_changes_data'),
    path('repository/<str:repository_name>/', svn_repository_home, name='repository_home'),
    path('commit/<int:commit_id>', svn_commit_details, name='svn_commit_details'),


]
