from rest_framework import serializers

from svn.models import FileChange


class FileChangeQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChange
        fields = ['id', 'commit', 'path', 'action', 'kind', ]
    