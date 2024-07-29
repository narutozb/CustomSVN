from rest_framework import serializers
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


class FileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChange
        fields = ['id', 'path', 'action', 'kind', 'commit']


class CommitSerializer(serializers.ModelSerializer):
    file_changes_count = serializers.IntegerField(source='file_changes.count', read_only=True)
    repository = RepositorySerializer(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = Commit
        fields = ['id', 'revision', 'author', 'message', 'date', 'file_changes_count', 'repository', 'branch']


class CommitQuerySerializer(serializers.Serializer):
    repositories = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    branches = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )


class CommitDetailSerializer(serializers.ModelSerializer):
    file_changes = FileChangeSerializer(many=True, read_only=True)
    repository = RepositorySerializer(read_only=True, required=False)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = Commit
        fields = ['id', 'revision', 'author', 'date', 'message', 'file_changes', 'repository', 'branch', ]
