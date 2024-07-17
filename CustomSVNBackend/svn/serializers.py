from rest_framework import serializers
from .models import Repository, Commit, FileChange


class QueryFileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChange
        fields = ['path', 'action', 'id', 'commit']

    def get_view_file_path(self, obj):
        return f"File: {obj.path}"


class FileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChange
        fields = ['path', 'action', 'kind']


class CommitSerializer(serializers.ModelSerializer):
    file_changes_count = serializers.IntegerField(source='file_changes.count', read_only=True)

    class Meta:
        model = Commit
        fields = ['id', 'revision', 'author', 'message', 'date', 'file_changes_count']


class RepositorySerializer(serializers.ModelSerializer):
    commits_count = serializers.IntegerField(source='commits.count', read_only=True)

    class Meta:
        model = Repository
        fields = ['id', 'name', 'url', 'description', 'created_at', 'commits_count']


class VerifyRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['name', 'url']
