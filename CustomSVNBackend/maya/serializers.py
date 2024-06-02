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
    transform_nodes = TransformNodeSerializer(many=True, required=False, )
    shape_nodes = ShapeNodeSerializer(many=True, required=False, )
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    local_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = MayaFile
        fields = '__all__'

    def create(self, validated_data):
        # print debug information
        print(f'---MayaFileSerializer---')

        scene_info_data = validated_data.pop('scene_info', None)
        transform_nodes_data = validated_data.pop('transform_nodes', [])
        shape_nodes_data = validated_data.pop('shape_nodes', [])

        maya_file, created = MayaFile.objects.get_or_create(
            changed_file=validated_data.get('changed_file'),
            defaults={**validated_data}
        )

        if created:
            if scene_info_data:
                scene_info = SceneInfo.objects.create(**scene_info_data)
                maya_file.scene_info = scene_info

            if transform_nodes_data:
                transform_nodes = [TransformNode.objects.create(**data) for data in transform_nodes_data]
                maya_file.transform_nodes.set(transform_nodes)

            if shape_nodes_data:
                shape_nodes = [ShapeNode.objects.create(**data) for data in shape_nodes_data]
                maya_file.shape_nodes.set(shape_nodes)

            maya_file.save()

        return maya_file

    def update(self, instance, validated_data):
        print(f'---MayaFileSerializer--- {"update" * 20}')
        scene_info_data = validated_data.pop('scene_info', None)

        client_version = validated_data.get('client_version') or '0.0.0'
        server_version = instance.client_version or '0.0.0'

        client_version = parse(client_version)
        server_version = parse(server_version)

        if client_version > server_version:
            # 更新实例的字段
            for attr, value in validated_data.items():
                if attr in ['transform_nodes', 'shape_nodes']:
                    getattr(instance, attr).set(value)
                else:
                    setattr(instance, attr, value)
            instance.save()

            if scene_info_data and instance.scene_info:
                # 更新关联的SceneInfo对象
                for attr, value in scene_info_data.items():
                    setattr(instance.scene_info, attr, value)
                instance.scene_info.save()

        elif client_version == server_version:
            raise serializers.ValidationError({"msg": "客户端版本为最新，无需更新数据"})
        else:
            raise serializers.ValidationError({"msg": "客户端版本已过时，请更新客户端"})

        return MayaFile.objects.get(id=instance.id)
