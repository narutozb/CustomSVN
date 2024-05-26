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


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance
