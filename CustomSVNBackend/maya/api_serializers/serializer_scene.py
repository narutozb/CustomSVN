from rest_framework import serializers

from maya.models import SceneInfo


class SceneQuerySerializerS(serializers.ModelSerializer):
    class Meta:
        model = SceneInfo
        fields = '__all__'

