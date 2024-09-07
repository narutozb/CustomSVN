import os.path

from rest_framework import serializers

from svn._serializers.serializer_base import SoloSerializer
from svn._serializers.serializer_commit import CommitQuerySerializer, CommitQuerySerializerS
from svn._serializers.serializer_repository import RepositoryQuerySerializerS
from svn.models import FileChange, Repository


class FileChangeQuerySerializerS(serializers.ModelSerializer):
    suffix = serializers.SerializerMethodField()

    class Meta:
        model = FileChange
        fields = ['id', 'commit', 'path', 'action', 'kind', ]


class FileChangeQuerySerializer(serializers.ModelSerializer):
    suffix = serializers.SerializerMethodField()
    commit = CommitQuerySerializerS(read_only=True)
    repository = serializers.SerializerMethodField()

    class Meta:
        model = FileChange
        fields = ['id', 'commit', 'path', 'action', 'kind', 'suffix', 'repository']

    def get_suffix(self, obj: FileChange):
        suffix = None
        if obj.kind == 'file':
            base_name = os.path.basename(obj.path)
            _, suffix = os.path.splitext(base_name)
        return suffix

    def get_repository(self, obj: FileChange):
        repo = Repository.objects.get(commits__file_changes=obj)
        d = RepositoryQuerySerializerS(instance=repo, read_only=True)
        return d.data


class FileChangeQuerySoloSerializer(SoloSerializer):
    suffix = serializers.SerializerMethodField()
    commit = CommitQuerySerializerS(read_only=True)
    repository = serializers.SerializerMethodField()

    class Meta:
        model = FileChange
        fields = ['id', 'commit', 'path', 'action', 'kind', 'suffix', 'repository']

    def get_suffix(self, obj: FileChange):
        suffix = None
        if obj.kind == 'file':
            base_name = os.path.basename(obj.path)
            _, suffix = os.path.splitext(base_name)
        return suffix

    def get_repository(self, obj: FileChange):
        repo = Repository.objects.get(commits__file_changes=obj)
        d = RepositoryQuerySerializerS(instance=repo, read_only=True)
        return d.data
