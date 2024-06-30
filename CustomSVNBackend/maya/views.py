from django.shortcuts import render, get_object_or_404
from packaging.version import parse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from svn.models import Repository, Commit, FileChange
from svn.views.views import CustomPagination
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
    print('list_maya_file_changes'.center(20, '*'))
    maya_client_version = request.GET.get('maya_client_version')
    client_version = parse(maya_client_version)
    try:
        repository = Repository.objects.get(name=repo_name)
        commit = Commit.objects.get(repository=repository, revision=revision)
        file_changes = FileChange.objects.filter(commit=commit)

        result_file_changes = []
        for fc in file_changes:
            if not hasattr(fc, 'maya_file') or parse(fc.maya_file.client_version) < client_version:
                result_file_changes.append(fc)

        if not result_file_changes:
            return Response({'status': 'success', 'message': 'Client version is up-to-date'}, status=status.HTTP_200_OK)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(result_file_changes, request)

        file_change_list = [{'file_path': change.path, 'change_type': change.action, 'id': change.id} for
                            change in
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
        # print(request.data)
        changed_file = request.data.get('changed_file')
        maya_file = MayaFile.objects.filter(changed_file=changed_file).first()

        serializer = MayaFileSerializer(maya_file, data=request.data) if maya_file else MayaFileSerializer(
            data=request.data)

        if serializer.is_valid():
            if maya_file:
                serializer.update(maya_file, serializer.validated_data)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def maya_file_view(request, file_change_id):
    maya_file = get_object_or_404(MayaFile, changed_file_id=file_change_id)
    return render(request, 'maya/maya_file_details.html', {'maya_file': maya_file})
