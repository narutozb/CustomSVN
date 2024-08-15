from rest_framework import serializers

from character.models import Tag


class CharacterTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'description', 'active')
