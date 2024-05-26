from rest_framework import serializers
from .models import MayaFile, FileAttribute, SceneInfo, TransformNode, ShapeNode

class FileAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttribute
        fields = '__all__'

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
    file_attribute = FileAttributeSerializer()
    scene_info = SceneInfoSerializer()

    class Meta:
        model = MayaFile
        fields = '__all__'
