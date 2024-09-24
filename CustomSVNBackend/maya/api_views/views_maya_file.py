from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from maya.api_serializers.serializer_maya_file import MayaFileQuerySerializerS, BulkMayaFileSerializer, \
    MayaFileQuerySerializer
from django.db.models import OuterRef, Exists

from django_filters import rest_framework as filters
from maya.models import MayaFile
from svn.models import Commit, FileChange, Repository, Branch

from svn._serializers.serializer_commit import CommitQuerySerializerS


class MayaFileFilter(filters.FilterSet):
    repository_id = filters.NumberFilter(field_name='changed_file__commit__repository__id')
    commit_id = filters.NumberFilter(field_name='changed_file__commit__id')
    file_change_ids = filters.CharFilter(method='filter_by_file_change_ids', label='FileChangesID')

    class Meta:
        model = MayaFile
        fields = ['repository_id', 'commit_id', 'file_change_ids']

    def filter_by_file_change_ids(self, queryset, name, value):
        file_change_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
        return queryset.filter(changed_file__id__in=file_change_ids)


class MayaFileQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MayaFile.objects.all()
    serializer_class = MayaFileQuerySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MayaFileFilter  # 使用我们的自定义过滤器

    @action(detail=False, methods=['get'])
    def orphan_file_changes(self, request):
        '''
        用于获取没有对应MayaFile的FileChange
        '''
        commit_id = request.query_params.get('commit_id')
        if not commit_id:
            return Response({"error": "commit_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            commit = Commit.objects.get(id=commit_id)
        except Commit.DoesNotExist:
            return Response({"error": "Commit not found"}, status=status.HTTP_404_NOT_FOUND)

        orphan_file_changes = FileChange.objects.filter(commit=commit).exclude(
            Exists(MayaFile.objects.filter(changed_file=OuterRef('pk')))
        )

        # You might want to create a serializer for FileChange if you haven't already
        data = [{
            'id': fc.id,
            'path': fc.path,
            'action': fc.action,
            'kind': fc.kind
        } for fc in orphan_file_changes]

        return Response(data)

    @action(detail=False, methods=['get'])
    def earliest_commit_without_mayafile(self, request):
        """
        用于获取包含.ma或.mb文件但没有对应MayaFile的最早的Commit
        作为判断是否需要导入MayaFile的依据
        GET参数:
        branch_id: 分支ID

        """
        branch_id = request.query_params.get('branch_id')
        if not branch_id:
            return Response({"error": "branch_id  is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            branch = Branch.objects.get(id=branch_id)

        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        # 查找包含.ma或.mb文件但没有对应MayaFile的最早的Commit
        earliest_commit = Commit.objects.filter(
            branch=branch,
            file_changes__kind='file',
            file_changes__path__regex=r'.*\.(ma|mb)$',
            file_changes__action__in=['A', 'M'],

        ).exclude(
            Exists(
                MayaFile.objects.filter(
                    changed_file__commit=OuterRef('pk'),
                    changed_file__kind='file',
                    changed_file__path__regex=r'.*\.(ma|mb)$',
                    changed_file__action__in=['A', 'M'],
                )
            )
        ).order_by('revision').first()

        if not earliest_commit:
            return Response({"message": "All .ma and .mb files in this repository have associated MayaFiles"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = CommitQuerySerializerS(earliest_commit)

        return Response(serializer.data)


class MayaFileCommandViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = MayaFile.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BulkMayaFileSerializer
        return MayaFileQuerySerializerS

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maya_files = serializer.save()
        return Response(MayaFileQuerySerializerS(maya_files, many=True).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maya_files = serializer.save()
        return Response(MayaFileQuerySerializerS(maya_files, many=True).data, status=status.HTTP_200_OK)
