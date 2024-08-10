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
    gender = serializers.PrimaryKeyRelatedField(queryset=Gender.objects.all(), required=False, allow_null=True)
    race = serializers.PrimaryKeyRelatedField(queryset=Race.objects.all(), required=False, allow_null=True)
    gender_name = serializers.CharField(source='gender.name', read_only=True)
    race_name = serializers.CharField(source='race.name', read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    items = CharacterItemSerializer(source='characteritem_set', many=True, read_only=True)
    thumbnails = ThumbnailSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = ['id', 'name', 'character_id', 'description', 'height', 'gender', 'gender_name', 'race', 'race_name',
                  'tags', 'items', 'thumbnails']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        instance = super().create(validated_data)
        instance.tags.set(tags)
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.set(tags)
        return instance
