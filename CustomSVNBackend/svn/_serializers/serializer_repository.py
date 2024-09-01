from rest_framework import serializers

from svn.models import Repository, FileChange


class RepositoryQuerySerializer(serializers.ModelSerializer):
    total_commits = serializers.IntegerField(source='commits.count', read_only=True)
    total_file_changes = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = ['id', 'name', 'description', 'url', 'total_commits', 'total_file_changes']

    def get_total_file_changes(self, obj):
        return FileChange.objects.filter(commit__repository=obj).count()
