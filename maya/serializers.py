from packaging.version import Version, parse

from rest_framework import serializers
from .models import MayaFile, SceneInfo, TransformNode, ShapeNode


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
    scene_info = SceneInfoSerializer(required=False)
    transform_nodes = TransformNodeSerializer(many=True)
    shape_nodes = ShapeNodeSerializer(many=True, )
    status = serializers.CharField(required=False, allow_blank=True)
    local_path = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = MayaFile
        fields = '__all__'

    def create(self, validated_data):
        print('-'*20)
        scene_info_data = validated_data.pop('scene_info', None)
        transform_nodes_data = validated_data.pop('transform_nodes', None)
        shape_nodes_data = validated_data.pop('shape_nodes', None)
        print('尝试创建MayaFile')
        scene_info = SceneInfoSerializer.create(SceneInfoSerializer(),
                                                validated_data=scene_info_data) if scene_info_data else None
        maya_file, created = MayaFile.objects.get_or_create(
            changed_file=validated_data.get('changed_file'),
            defaults={'scene_info': scene_info, **validated_data}
        )
        print(f'数据存在状况:{created}')
        if not created:

            client_version = parse(validated_data.get('client_version'))
            server_version = parse(maya_file.client_version)

            if not isinstance(server_version, Version):
                server_version = parse('0.0.0')

            if client_version > server_version:
                for attr, value in validated_data.items():
                    setattr(maya_file, attr, value)
                maya_file.save()
            else:
                raise serializers.ValidationError({"msg": "客户端版本过旧不接受此数据"})

        return maya_file
