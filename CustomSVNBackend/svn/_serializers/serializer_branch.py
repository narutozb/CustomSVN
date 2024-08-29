from rest_framework import serializers

from svn.models import Branch


class BranchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "name", "repository"]
