from django.db.models import Max
from rest_framework import serializers

from svn._serializers.serializer_base import SoloSerializer
from svn._serializers.serializer_branch import BranchQuerySerializer
from svn.models import Repository, FileChange, Commit, Branch


class RepositoryQuerySerializerS(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'name', 'description', 'created_at', 'url', ]


class RepositoryQuerySerializer(serializers.ModelSerializer):
    total_commits = serializers.IntegerField(source='commits.count', read_only=True)
    total_file_changes = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = ['id', 'name', 'description', 'created_at', 'url', 'total_commits', 'total_file_changes']

    def get_total_file_changes(self, obj):
        return FileChange.objects.filter(commit__repository=obj).count()


class RepositoryQuerySoloSerializer(SoloSerializer):
    total_commits = serializers.IntegerField(source='commits.count', read_only=True)
    total_file_changes = serializers.SerializerMethodField(read_only=True)
    authors = serializers.SerializerMethodField(read_only=True)
    branches = BranchQuerySerializer(read_only=True, required=False)

    class Meta:
        model = Repository
        fields = ['id', 'name', 'description', 'created_at', 'url', 'total_commits', 'total_file_changes',
                  'authors', 'branches']

    def get_total_file_changes(self, obj):
        return FileChange.objects.filter(commit__repository=obj).count()

    def get_authors(self, obj):
        commits = Commit.objects.filter(repository=obj)
        authors = commits.values('author').annotate(
            max_id=Max('id')
        ).values_list('author', flat=True)
        return authors


class RepositoryCommitSearchFilterSerializer(serializers.ModelSerializer):
    '''
    Commit搜索页面的过滤其必要数据.通过Repository获取
    '''
    class __BranchQuerySerializer(serializers.ModelSerializer):
        class Meta:
            model = Branch
            fields = ["id", "name", ]

    branches = __BranchQuerySerializer(many=True, read_only=True)
    authors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Repository
        fields = ['id', 'name', 'url', 'description', 'branches', 'authors']

    def get_authors(self, obj):
        commits = Commit.objects.filter(repository=obj)
        authors = commits.values('author').annotate(
            max_id=Max('id')
        ).values_list('author', flat=True)
        return authors
