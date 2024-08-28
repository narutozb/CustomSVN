from rest_framework import serializers

from svn.models import Commit


class CommitQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commit
        fields = ['id', 'revision', 'branch', 'message', 'author', 'date']


