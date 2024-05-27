from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.utils import timezone
from svn.models import Repository, Commit, FileChange
from maya.models import MayaFile, SceneInfo, TransformNode, ShapeNode

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

        # 创建 SceneInfo 对象
        scene_info = SceneInfo.objects.create(
            transforms=5,
            groups=2,
            empty_groups=1,
            meshes=10,
            verts=100,
            edges=15,
            faces=50,
            tris=75,
            uvs=200,
            ngons=3,
            materials=4,
            textures=2,
            cameras=1,
            joints=6,
            lights=3,
            blend_shapes=1,
            morph_targets=2,
            nurbs_curves=1,
            root_nodes=5,
            up_axis='Y',
            linear='cm',
            angular='deg',
            current_time=24.0,
            anim_start_time=0.0,
            anim_end_time=100.0,
            play_back_start_time=0.0,
            play_back_end_time=100.0,
            frame_rate=24.0
        )

        # 创建 TransformNode 对象
        transform_node = TransformNode.objects.create(
            scene=scene_info,
            node_name='Node0|NodeA',
            transform_property='translateX',
            translate_x=1.0,
            translate_y=2.0,
            translate_z=3.0,
            rotate_x=0.0,
            rotate_y=0.0,
            rotate_z=0.0,
            scale_x=1.0,
            scale_y=1.0,
            scale_z=1.0,
            parent=None
        )

        # 创建 ShapeNode 对象
        shape_node = ShapeNode.objects.create(
            scene=scene_info,
            node_name='Node0|NodeB',
            shape_property='polygon',
            parent=None
        )

        # 创建 MayaFile 对象
        maya_file = MayaFile.objects.create(
            changed_file=file_change,
            status='opened',
            description='This is a test file.',
            local_path='/path/to/test/file.mb',
            scene_info=scene_info
        )

        # 为 MayaFile 添加节点属性
        maya_file.transform_nodes.add(transform_node)
        maya_file.shape_nodes.add(shape_node)

        self.stdout.write(self.style.SUCCESS('Successfully added test data'))
