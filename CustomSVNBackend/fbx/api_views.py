from packaging.version import parse

from rest_framework.response import Response
from rest_framework.views import APIView

from svn.models import FileChange, Repository
from svn.query_functions.functions import verify_repo, verify_svn_data
from svn.serializers import QueryFileChangeSerializer, VerifyRepositorySerializer
# Create your views here.
from .models import FBXFile, Take, ModelSkeleton, TakeModelSkeleton
from rest_framework import generics, permissions, viewsets
from .serializers import FBXFileSerializer, TakeSerializer, ModelSkeletonSerializer, TakeModelSkeletonSerializer, \
    ReceiveFBXFileSerializer, ReceiveTakeSerializer, ReceiveModelSkeleton


class FBXFileList(generics.ListCreateAPIView):
    queryset = FBXFile.objects.all()
    serializer_class = FBXFileSerializer


class FBXFileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FBXFile.objects.all()
    serializer_class = FBXFileSerializer


class TakeList(generics.ListCreateAPIView):
    queryset = Take.objects.all()
    serializer_class = TakeSerializer


class TakeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Take.objects.all()
    serializer_class = TakeSerializer


class ModelSkeletonList(generics.ListCreateAPIView):
    queryset = ModelSkeleton.objects.all()
    serializer_class = ModelSkeletonSerializer


class ModelSkeletonDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ModelSkeleton.objects.all()
    serializer_class = ModelSkeletonSerializer


class TakeModelSkeletonList(generics.ListCreateAPIView):
    queryset = TakeModelSkeleton.objects.all()
    serializer_class = TakeModelSkeletonSerializer


def save_model_skeletons(model_skeletons, fbx_file):
    parent_map = {}

    # First pass: create all skeletons without setting the parent field
    for skeleton_data in model_skeletons:
        parent_name = skeleton_data.pop('parent', None)
        skeleton, created = ModelSkeleton.objects.get_or_create(name=skeleton_data['name'], fbx_file=fbx_file)

        if parent_name:
            parent_map[skeleton.name] = parent_name

    # Refresh the saved_skeletons dictionary from the database
    saved_skeletons = {skeleton.name: skeleton for skeleton in ModelSkeleton.objects.filter(fbx_file=fbx_file)}

    # Second pass: set the parent field for all skeletons
    for skeleton_name, parent_name in parent_map.items():
        skeleton = saved_skeletons[skeleton_name]
        parent = saved_skeletons[parent_name]
        skeleton.parent = parent
        skeleton.save()


class ReceiveFbxFileData(APIView):
    '''
    返回所有FBXFile的serializer数据

    {
        "fps": 30.0,
        "file_change": 8150 // file_change_id
    }
    '''

    def get(self, request, *args, **kwargs):

        fbx_files = FBXFile.objects.all()
        serializer = FBXFileSerializer(fbx_files, many=True)
        return Response(serializer.data)

    def post(self, request):
        print('post')
        data = request.data
        change_file_data = data.get('change_file')
        fbx_data = data.get('fbx_data')
        repo_data = data.get('repo_data')
        takes: list[dict] = data.get('takes')
        model_skeletons: list[dict] = data.get('skeletons')
        # 验证repo数据
        repo: Repository = verify_svn_data(repo_data, Repository)
        if not repo:
            return Response({'msg': 'Repo验证失败', })

        # 验证FileChange
        try:
            file_change = FileChange.objects.get(
                commit__repository=repo,
                commit__revision=change_file_data.get('revision'),
                path=change_file_data.get('path')
            )
        except Exception as e:
            return Response({'msg': str(e), })

        try:
            # 创建FBXFile
            # 1. 更新fbx_file数据
            fbx_file, fbx_file_created = FBXFile.objects.get_or_create(file_change=file_change)
            serializer = ReceiveFBXFileSerializer(instance=fbx_file, data=fbx_data)
            if serializer.is_valid():
                serializer.save()

            for i in takes:
                i['fbx_file'] = fbx_file.id

            take_serializer = ReceiveTakeSerializer(data=takes, many=True)
            if take_serializer.is_valid(raise_exception=True):
                if fbx_file_created:
                    take_serializer.save()


            #     # 3. 储存skeleton数据
            print('开始储存skeleton数据')
            # 创建根节点
            ModelSkeleton.objects.get_or_create(name='RootNode', fbx_file=fbx_file, parent=None)
            # 储存ModelSkeleton
            save_model_skeletons(model_skeletons, fbx_file)

            return Response({'success': 'FBXFile created successfully', 'data': serializer.data})

        except Exception as e:
            return Response({'error': str(e)})
