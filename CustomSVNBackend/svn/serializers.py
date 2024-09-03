from rest_framework import serializers
from rest_framework.decorators import action

from ._serializers.serializer_branch import BranchQuerySerializer
from ._serializers.serializer_commit import CommitQuerySerializerS, CommitQuerySerializer
from ._serializers.serializer_file_change import FileChangeQuerySerializer
from ._serializers.serializer_repository import RepositoryQuerySerializer, RepositoryQuerySerializerS
from .models import Repository, Commit, FileChange, Branch


class RepositorySerializer(serializers.ModelSerializer):
    commits_count = serializers.IntegerField(source='commits.count', read_only=True)

    class Meta:
        model = Repository
        fields = ['id', 'name', 'url', 'description', 'created_at', 'commits_count']


class QueryFileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChange
        fields = ['path', 'action', 'id', 'commit']

    def get_view_file_path(self, obj):
        return f"File: {obj.path}"


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'repository']


class CommitSerializer(serializers.ModelSerializer):
    file_changes_count = serializers.IntegerField(source='file_changes.count', read_only=True)
    repository = RepositorySerializer(read_only=True)
    branch = BranchQuerySerializer(read_only=True)

    class Meta:
        model = Commit
        fields = ['id', 'revision', 'author', 'message', 'date', 'file_changes_count', 'repository', 'branch']


class FileChangeSerializer(serializers.ModelSerializer):
    commit = CommitQuerySerializer(read_only=True)
    repository = RepositoryQuerySerializerS(read_only=True)

    class Meta:
        model = FileChange
        fields = ['id', 'path', 'action', 'kind', 'commit', 'repository']

    def get_repository(self, obj):
        return RepositorySerializer(obj.commit.repository).data


class CommitDetailSerializer(serializers.ModelSerializer):
    file_changes = FileChangeQuerySerializer(many=True, read_only=True)
    repository = RepositoryQuerySerializerS(read_only=True)
    branch = BranchQuerySerializer(read_only=True)

    class Meta:
        model = Commit
        fields = ['id', 'revision', 'author', 'date', 'message', 'file_changes', 'repository', 'branch']
