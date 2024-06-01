from requests import Response
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from svn.models import Repository, Commit, FileChange
from svn.views import CustomPagination
from .models import MayaFile, SceneInfo, TransformNode, ShapeNode
from .serializers import MayaFileSerializer, SceneInfoSerializer, TransformNodeSerializer, ShapeNodeSerializer


class MayaFileViewSet(viewsets.ModelViewSet):
    queryset = MayaFile.objects.all()
    serializer_class = MayaFileSerializer


class SceneInfoViewSet(viewsets.ModelViewSet):
    queryset = SceneInfo.objects.all()
    serializer_class = SceneInfoSerializer


class TransformNodeViewSet(viewsets.ModelViewSet):
    queryset = TransformNode.objects.all()
    serializer_class = TransformNodeSerializer


class ShapeNodeViewSet(viewsets.ModelViewSet):
    queryset = ShapeNode.objects.all()
    serializer_class = ShapeNodeSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_maya_file_changes(request, repo_name, revision, ):
    maya_client_version = request.GET.get('maya_client_version')
    try:
        repository = Repository.objects.get(name=repo_name)
        commit = Commit.objects.get(repository=repository, revision=revision)
        file_changes = FileChange.objects.filter(
            commit=commit,
            maya_file__isnull=True,
        ).exclude(maya_file__client_version=maya_client_version)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(file_changes, request)

        file_change_list = [{'file_path': change.file_path, 'change_type': change.change_type} for change in
                            result_page]
        return paginator.get_paginated_response(file_change_list)
    except (Repository.DoesNotExist, Commit.DoesNotExist):
        return Response(
            {
                'status': 'error', 'message': 'Repository or Commit does not exist'
            },
            status=status.HTTP_404_NOT_FOUND
        )


class MayaFileView(APIView):
    def post(self, request, format=None):
        serializer = MayaFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
