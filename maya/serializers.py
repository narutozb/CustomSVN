from rest_framework import serializers
from .models import MayaFile,  SceneInfo, TransformNode, ShapeNode



class SceneInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SceneInfo
        fields = '__all__'

class TransformNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransformNode
        fields = '__all__'

class ShapeNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShapeNode
        fields = '__all__'

class MayaFileSerializer(serializers.ModelSerializer):
    scene_info = SceneInfoSerializer()
    transform_nodes = TransformNodeSerializer(many=True)
    shape_nodes = ShapeNodeSerializer(many=True)

    class Meta:
        model = MayaFile
        fields = '__all__'
