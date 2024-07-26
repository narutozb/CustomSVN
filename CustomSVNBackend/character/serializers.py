from rest_framework import serializers
from .models import Gender, Race, Tag, Item, ItemAttribute, Character, CharacterItem, CharacterItemAttribute, Thumbnail

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['id', 'name']

class RaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Race
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description']

class ItemAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAttribute
        fields = ['id', 'name']

class CharacterItemAttributeSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = CharacterItemAttribute
        fields = ['id', 'attribute', 'attribute_name', 'value']

class CharacterItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    attributes = CharacterItemAttributeSerializer(source='characteritemattribute_set', many=True, read_only=True)

    class Meta:
        model = CharacterItem
        fields = ['id', 'item', 'item_name', 'attributes']

class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ['id', 'image']

class CharacterSerializer(serializers.ModelSerializer):
    gender_name = serializers.CharField(source='gender.name', read_only=True)
    race_name = serializers.CharField(source='race.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    items = CharacterItemSerializer(source='characteritem_set', many=True, read_only=True)
    thumbnails = ThumbnailSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = ['id', 'name', 'character_id', 'description', 'height', 'gender', 'gender_name', 'race', 'race_name', 'tags', 'items', 'thumbnails']