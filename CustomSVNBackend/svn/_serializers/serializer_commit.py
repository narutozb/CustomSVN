from rest_framework import serializers

from svn._serializers.serializer_branch import BranchQuerySerializer
from svn._serializers.serializer_repository import RepositoryQuerySerializer, RepositoryQuerySerializerS
from svn.models import Commit


class CommitQuerySerializerS(serializers.ModelSerializer):
    class Meta:
        model = Commit
        fields = ['id', 'revision', 'branch', 'message', 'author', 'date']


class CommitQuerySerializer(serializers.ModelSerializer):
    total_file_changes = serializers.IntegerField(source='file_changes.count', read_only=True)
    repository = RepositoryQuerySerializerS(read_only=True)
    branch = BranchQuerySerializer(read_only=True)

    class Meta:
        model = Commit
        fields = ['id', 'revision', 'author', 'message', 'date', 'total_file_changes', 'repository', 'branch']


class CommitPreviewSerializer(serializers.ModelSerializer):
    '''
    在Commit搜索页面使用的Hover预览
    '''

    class Meta:
        model = Commit
        fields = [
            'revision', 'author', 'date',
        ]
