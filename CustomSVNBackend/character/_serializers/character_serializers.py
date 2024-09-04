from rest_framework import serializers

from character.models import Character, Gender


class CharacterQueryCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ('id', 'name', 'character_id', 'description', 'height', 'gender', 'race', 'tags', 'description')


class CharacterCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ('name', 'character_id', 'description', 'height', 'gender', 'race', 'tags')

    def save(self, **kwargs):
        print('before-save')
        super().save(**kwargs)
        print('after-save')

    def update(self, instance, validated_data):
        print('before-update')
        inst = super().update(instance, validated_data)
        print('after-update')
        return inst
