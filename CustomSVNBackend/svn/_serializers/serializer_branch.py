from django.db.models import Max
from rest_framework import serializers

from svn.models import Branch, Commit, FileChange


class BranchQueryDetailSerializer(serializers.ModelSerializer):
    total_commits = serializers.SerializerMethodField()
    total_file_changes = serializers.SerializerMethodField()
    total_authors = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = ["id", "name", "repository", "total_commits",
                  "total_file_changes", "total_authors"
                  ]

    def get_total_commits(self, obj):
        return Commit.objects.filter(branch=obj).count()

    def get_total_file_changes(self, obj):
        return FileChange.objects.filter(commit__branch=obj).count()

    def get_total_authors(self, obj):
        authors = Commit.objects.filter(branch=obj).values('author').annotate(
            max_id=Max('id')
        ).values_list('author', flat=True)
        return authors
