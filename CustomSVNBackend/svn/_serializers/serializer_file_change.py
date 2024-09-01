import os.path

from rest_framework import serializers

from svn.models import FileChange


class FileChangeQuerySerializer(serializers.ModelSerializer):
    suffix = serializers.SerializerMethodField()

    class Meta:
        model = FileChange
        fields = ['id', 'commit', 'path', 'action', 'kind', 'suffix']

    def get_suffix(self, obj: FileChange):
        suffix = None
        if obj.kind == 'file':
            base_name = os.path.basename(obj.path)
            _, suffix = os.path.splitext(base_name)
        return suffix
