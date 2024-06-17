from .api_views import FBXFileList, TakeList, ModelSkeletonList, TakeModelSkeletonList, ReceiveFbxFileData
from django.urls import path

urlpatterns = [
    path('fbxfiles/', FBXFileList.as_view()),

    path('takes/', TakeList.as_view()),
    path('modelskeletons/', ModelSkeletonList.as_view()),
    path('takemodelskeletons/', TakeModelSkeletonList.as_view()),
    path('receive_fbx_file_data/', ReceiveFbxFileData.as_view()),
]
