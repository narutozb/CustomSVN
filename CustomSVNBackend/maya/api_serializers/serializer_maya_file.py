from rest_framework import serializers
from maya.models import MayaFile, FileChange
from svn.models import Repository


class MayaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MayaFile
        fields = ('id', 'changed_file', 'opened_successfully', 'status', 'description', 'local_path', 'client_version')


class MayaFileCommandSerializer(serializers.Serializer):
    repository_name = serializers.CharField(max_length=100)
    commit_revision = serializers.IntegerField()
    path = serializers.CharField(max_length=255)
    opened_successfully = serializers.BooleanField(required=False, allow_null=True)
    status = serializers.CharField(max_length=50, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    local_path = serializers.CharField(max_length=255, required=False, allow_null=True)
    client_version = serializers.CharField(max_length=64, required=False, allow_null=True)

    def create_or_update_maya_file(self, validated_data):
        repository_name = validated_data['repository_name']
        commit_revision = validated_data['commit_revision']
        path = validated_data['path']

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
            return maya_file
        except (Repository.DoesNotExist, FileChange.DoesNotExist):
            raise serializers.ValidationError(f"Invalid data for repository {repository_name} or file path {path}.")

class BulkMayaFileSerializer(serializers.Serializer):
    maya_files = MayaFileCommandSerializer(many=True)

    def create(self, validated_data):
        maya_files_data = validated_data['maya_files']
        maya_files = []
        for maya_file_data in maya_files_data:
            maya_file = MayaFileCommandSerializer().create_or_update_maya_file(maya_file_data)
            maya_files.append(maya_file)
        return maya_files

    def update(self, instance, validated_data):
        return self.create(validated_data)