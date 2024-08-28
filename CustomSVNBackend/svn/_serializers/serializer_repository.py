from rest_framework import serializers

from svn.models import Repository


class RepositoryQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'name', 'description', 'url']
