from rest_framework import serializers
from django.db import transaction

from svn.models import Repository, FileChange
from ..models import TransformNode, SceneInfo, MayaFile

class TransformNodeSerializer(serializers.ModelSerializer):
    parent = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = TransformNode
        exclude = ('scene',)

class SceneInfoSerializer(serializers.ModelSerializer):
    transform_nodes = TransformNodeSerializer(many=True)

    class Meta:
        model = SceneInfo
        exclude = ('maya_file',)

class MayaFileOutputSerializer(serializers.ModelSerializer):
    repository_name = serializers.SerializerMethodField()
    commit_revision = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    scene_info = SceneInfoSerializer()

    class Meta:
        model = MayaFile
        fields = ('id', 'repository_name', 'commit_revision', 'path', 'opened_successfully', 'status', 'description', 'local_path', 'client_version', 'scene_info')

    def get_repository_name(self, obj):
        return obj.changed_file.commit.repository.name

    def get_commit_revision(self, obj):
        return obj.changed_file.commit.revision

    def get_path(self, obj):
        return obj.changed_file.path

class ExtendedMayaFileSerializer(serializers.Serializer):
    repository_name = serializers.CharField(max_length=100)
    commit_revision = serializers.IntegerField()
    path = serializers.CharField(max_length=255)
    opened_successfully = serializers.BooleanField(required=False, allow_null=True)
    status = serializers.CharField(max_length=50, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    local_path = serializers.CharField(max_length=255, required=False, allow_null=True)
    client_version = serializers.CharField(max_length=64, required=False, allow_null=True)
    scene_info = SceneInfoSerializer(required=False)

    @transaction.atomic
    def create_or_update_maya_file(self, validated_data):
        repository_name = validated_data['repository_name']
        commit_revision = validated_data['commit_revision']
        path = validated_data['path']
        scene_info_data = validated_data.pop('scene_info', None)

        try:
            repository = Repository.objects.get(name=repository_name)
            file_change = FileChange.objects.get(
                commit__repository=repository,
                commit__revision=commit_revision,
                path=path
            )
            maya_file, created = MayaFile.objects.update_or_create(
                changed_file=file_change,
                defaults={
                    'opened_successfully': validated_data.get('opened_successfully'),
                    'status': validated_data.get('status'),
                    'description': validated_data.get('description'),
                    'local_path': validated_data.get('local_path'),
                    'client_version': validated_data.get('client_version'),
                }
            )

            if scene_info_data:
                transform_nodes_data = scene_info_data.pop('transform_nodes', [])
                scene_info, _ = SceneInfo.objects.update_or_create(
                    maya_file=maya_file,
                    defaults=scene_info_data
                )

                # Delete all existing TransformNodes for this SceneInfo
                TransformNode.objects.filter(scene=scene_info).delete()

                # Create new TransformNodes
                nodes = {}
                for node_data in transform_nodes_data:
                    parent_name = node_data.pop('parent', None)
                    node = TransformNode.objects.create(
                        scene=scene_info,
                        **node_data
                    )
                    nodes[node.node_name] = {'node': node, 'parent_name': parent_name}

                # Set parent relationships
                for node_name, node_info in nodes.items():
                    if node_info['parent_name']:
                        parent_node = nodes.get(node_info['parent_name'])
                        if parent_node:
                            node_info['node'].parent = parent_node['node']
                            node_info['node'].save()

            return maya_file
        except (Repository.DoesNotExist, FileChange.DoesNotExist) as e:
            raise serializers.ValidationError(f"Invalid data: {str(e)}")

class BulkExtendedMayaFileSerializer(serializers.Serializer):
    maya_files = ExtendedMayaFileSerializer(many=True)

    def create(self, validated_data):
        maya_files_data = validated_data['maya_files']
        maya_files = []
        for maya_file_data in maya_files_data:
            maya_file = ExtendedMayaFileSerializer().create_or_update_maya_file(maya_file_data)
            maya_files.append(maya_file)
        return maya_files

    def update(self, instance, validated_data):
        return self.create(validated_data)
# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response


class ExtendedMayaFileCommandViewSet(viewsets.GenericViewSet):
    queryset = MayaFile.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BulkExtendedMayaFileSerializer
        return MayaFileOutputSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maya_files = serializer.save()
        return Response(MayaFileOutputSerializer(maya_files, many=True).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maya_files = serializer.save()
        return Response(MayaFileOutputSerializer(maya_files, many=True).data, status=status.HTTP_200_OK)

