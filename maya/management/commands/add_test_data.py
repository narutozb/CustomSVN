from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.utils import timezone
from svn.models import Repository, Commit, FileChange
from maya.models import MayaFile, FileAttribute, SceneInfo, TransformNode, ShapeNode


class Command(BaseCommand):
    help = 'Add test data to the database'

    def handle(self, *args, **kwargs):
        # 创建 Repository 对象
        repository = Repository.objects.create(
            name=get_random_string(10),
            url='https://example.com/repo'
        )

        # 创建 Commit 对象
        commit = Commit.objects.create(
            repository=repository,
            revision=1,
            message='Initial commit',
            date=timezone.now()
        )

        # 创建 FileChange 对象
        file_change = FileChange.objects.create(
            commit=commit,
            file_path=get_random_string(10),
            change_type='modified'
        )

        # 创建 FileAttribute 对象
        file_attribute = FileAttribute.objects.create(
            status='opened',
            description='This is a test file.',
            local_path='/path/to/test/file.mb'
        )

        # 创建 SceneInfo 对象
        scene_info = SceneInfo.objects.create(
            transforms=5,
            groups=2,
            empty_groups=1,
            meshes=10,
            edges=15,
            up_axis='Y',
            linear='cm',
            current_time=24.0,
            anim_start_time=0.0,
            frame_rate=24.0
        )

        # 创建 TransformNode 对象
        transform_node = TransformNode.objects.create(
            scene=scene_info,
            node_name='Node0|NodeA',
            transform_property='translateX'
        )

        # 创建 ShapeNode 对象
        shape_node = ShapeNode.objects.create(
            scene=scene_info,
            node_name='Node0|NodeA',
            shape_property='polygon'
        )

        # 创建 MayaFile 对象
        maya_file = MayaFile.objects.create(
            changed_file=file_change,
            file_attribute=file_attribute,
            scene_info=scene_info
        )

        # 为 MayaFile 添加节点属性
        maya_file.transform_nodes.add(transform_node)
        maya_file.shape_nodes.add(shape_node)

        self.stdout.write(self.style.SUCCESS('Successfully added test data'))
