from rest_framework import serializers
from .models import Repository, Commit, FileChange
from django.contrib.auth.models import User


class FileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChange
        fields = ['file_path', 'change_type']

class CommitSerializer(serializers.ModelSerializer):
    file_changes_count = serializers.IntegerField(source='file_changes.count', read_only=True)

    class Meta:
        model = Commit
        fields = ['revision', 'author', 'message', 'date', 'file_changes_count']

class RepositorySerializer(serializers.ModelSerializer):
    commits_count = serializers.IntegerField(source='commits.count', read_only=True)

    class Meta:
        model = Repository
        fields = ['name', 'url', 'description', 'created_at', 'commits_count']
