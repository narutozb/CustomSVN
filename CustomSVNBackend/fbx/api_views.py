from packaging.version import parse

from rest_framework.response import Response
from rest_framework.views import APIView

from svn.models import FileChange
from svn.serializers import QueryFileChangeSerializer
# Create your views here.
from .models import FBXFile, Take, ModelSkeleton, TakeModelSkeleton
from rest_framework import generics, permissions, viewsets
from .serializers import FBXFileSerializer, TakeSerializer, ModelSkeletonSerializer, TakeModelSkeletonSerializer, \
    ReceiveFBXFileSerializer, ReceiveTakeSerializer


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
        takes: list[dict] = data.get('takes')
        # print(takes)
        file_change = FileChange.objects.get(
            commit__repository__name=change_file_data.get('repo_name'),
            commit__revision=change_file_data.get('revision'),
            file_path=change_file_data.get('file_path')
        )
        print('-' * 50)
        try:
            print('创建或者更新fbx_file')

            #  获取client_version
            client_version = fbx_data.get('client_version')
            client_version = parse(client_version)

            # 创建FBXFile
            fbx_file, fbx_file_created = FBXFile.objects.get_or_create(file_change_id=file_change.id, )
            print('FBXFile创建完成...')

            if parse(fbx_file.client_version) < client_version or fbx_file_created:
                print('新建数据或者服务器版本过低...')
                # 更新fbx_file数据

                serializer = ReceiveFBXFileSerializer(fbx_file, data=fbx_data)
                if serializer.is_valid():
                    serializer.save()

                # 创建 Take数据
                for i in takes:
                    i['fbx_file'] = fbx_file
                for take_data in takes:
                    Take.objects.get_or_create(**take_data)
                print('Takes创建完成...')

            serializer = ReceiveFBXFileSerializer(fbx_file)
            return Response({'success': 'FBXFile created successfully', 'data': serializer.data})

        except Exception as e:
            return Response({'error': str(e)})
