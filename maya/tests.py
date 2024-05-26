from django.test import TestCase
from django.utils.crypto import get_random_string
from django.utils import timezone
from svn.models import Repository, Commit, FileChange
from maya.models import MayaFile, FileAttribute, SceneInfo, TransformNode, ShapeNode

class MayaFileTest(TestCase):

    def setUp(self):
        # 创建 Repository 对象
        self.repository = Repository.objects.create(
            name=get_random_string(10),
            url='https://example.com/repo'
        )

        # 创建 Commit 对象
        self.commit = Commit.objects.create(
            repository=self.repository,
            revision=1,
            message='Initial commit',
            date=timezone.now()
        )

        # 创建 FileChange 对象
        self.file_change = FileChange.objects.create(
            commit=self.commit,
            file_path=get_random_string(10),
            change_type='modified'
        )

        # 创建 FileAttribute 对象
        self.file_attribute = FileAttribute.objects.create(
            status='opened',
            description='This is a test file.',
            local_path='/path/to/test/file.mb'
        )

        # 创建 SceneInfo 对象
        self.scene_info = SceneInfo.objects.create(
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
        self.transform_node = TransformNode.objects.create(
            scene=self.scene_info,
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
        self.shape_node = ShapeNode.objects.create(
            scene=self.scene_info,
            node_name='Node0|NodeB',
            shape_property='polygon',
            parent=None
        )

        # 创建 MayaFile 对象
        self.maya_file = MayaFile.objects.create(
            changed_file=self.file_change,
            file_attribute=self.file_attribute,
            scene_info=self.scene_info
        )

        # 为 MayaFile 添加节点属性
        self.maya_file.transform_nodes.add(self.transform_node)
        self.maya_file.shape_nodes.add(self.shape_node)

    def test_maya_file_creation(self):
        self.assertEqual(MayaFile.objects.count(), 1)
        self.assertEqual(FileAttribute.objects.count(), 1)
        self.assertEqual(SceneInfo.objects.count(), 1)
        self.assertEqual(TransformNode.objects.count(), 1)
        self.assertEqual(ShapeNode.objects.count(), 1)
        self.assertEqual(self.maya_file.transform_nodes.count(), 1)
        self.assertEqual(self.maya_file.shape_nodes.count(), 1)
        self.assertEqual(self.maya_file.scene_info.transforms, 5)
        self.assertEqual(self.maya_file.file_attribute.status, 'opened')
