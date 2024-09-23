from rest_framework import serializers

from maya.api_serializers.serializer_maya_file import MayaFileQuerySerializerS
from maya.functions import get_node_full_path
from maya.models import TransformNode
from svn._serializers.serializer_base import SoloSerializer


class TransformNodeQuerySerializerS(serializers.ModelSerializer):
    parent_node_name = serializers.CharField(source='parent.node_name', read_only=True)

    class Meta:
        model = TransformNode
        fields = ['id', 'scene', 'node_name', 'parent', 'parent_node_name']


class TransformNodeQuerySerializer(serializers.ModelSerializer):
    parent_node_name = serializers.CharField(source='parent.node_name', read_only=True)
    maya_file_id = serializers.CharField(source='scene.maya_file.id', read_only=True)
    full_node_name = serializers.SerializerMethodField()

    class Meta:
        model = TransformNode
        fields = '__all__'

    def get_full_node_name(self, obj: TransformNode):
        scene_id = obj.scene_id
        return get_node_full_path(obj.node_name, scene_id)


class TransformNodeSoloQuerySerializer(SoloSerializer):
    parent_node_name = serializers.CharField(source='parent.node_name', read_only=True)
    maya_file_details = serializers.SerializerMethodField()
    full_node_name = serializers.SerializerMethodField()

    class Meta:
        model = TransformNode
        fields = '__all__'

    def get_maya_file_details(self, obj: TransformNode):
        return MayaFileQuerySerializerS(instance=obj.scene.maya_file).data

    def get_full_node_name(self, obj: TransformNode):
        scene_id = obj.scene_id
        return get_node_full_path(obj.node_name, scene_id)
