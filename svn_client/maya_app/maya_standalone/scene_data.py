from dataclasses import dataclass

from custom_maya.custom_maya_class.scene_base import CMNode
from custom_maya.custom_maya_class.scene_property import CMFileOptions, CMStandaloneProperty
from custom_maya.custom_maya_class.scenefile_application import CMApplication, CustomSceneFunction
from custom_maya.tools.custom_maya_client.scene_utilities import SceneInformation
from maya import cmds


@dataclass
class FileOpenStatus:
    opened_successfully: bool
    opened_file_path: str
    detail: str = 'Opened successfully'


@dataclass
class FileCloseStatus:
    saved_successfully: bool
    saved_file_path: str
    detail: str = ''


class CustomCMApplication(CMNode, CMStandaloneProperty):
    '''maya应用'''

    def __init__(self, standalone_mode=True):
        super().__init__()
        self.standalone_mode = standalone_mode

    def standalone_maya(self):
        if self.is_standalone() and self.standalone_mode:
            '''当maya以独立模式运行时，需要初始化maya'''
            print("启动maya独立模式")
            import maya.standalone
            maya.standalone.initialize(name='python')

    def open_file(self, options: CMFileOptions):
        cmds.file(*options.get_open_file_options()[0], **options.get_open_file_options()[1])

    def save_file(self, options: CMFileOptions):
        cmds.file(*options.get_save_file_options()[0], **options.get_save_file_options()[1])


class SceneFileInformation:
    def __init__(self, open_file_option: CMFileOptions):
        self.app = CMApplication()
        self.open_file_option = open_file_option
        self.opened_file_status = self.open_scene_file()

    def open_scene_file(self) -> FileOpenStatus:
        open_file_options = self.open_file_option.get_open_file_options()
        file_path = open_file_options[0][0]
        try:
            print(f'尝试打开Maya文件:{file_path}')
            self.app.open_file(self.open_file_option)

        except RuntimeError as e:
            print('RuntimeError')
            if str(e).startswith('File not found:'):
                return FileOpenStatus(False, file_path, detail=str(e))

        except Exception as e:
            return FileOpenStatus(False, file_path, detail=str(e))

        return FileOpenStatus(True, file_path, )

    def get_data(self):
        if self.opened_file_status.opened_successfully:
            scene_information = SceneInformation().get_data()
        else:
            scene_information = {}

        return {
            'scene_file_information': self.opened_file_status.__dict__,
            'scene_information': scene_information
        }

    def get_transforms(self):
        scene_info = SceneInformation()
        result = []
        for i in scene_info.transform_manager.get_all_transforms():
            relatives = cmds.listRelatives(i.get_name(), parent=True)
            result.append({
                'node_name': i.get_name(),
                'parent': relatives[0] if relatives else None,
                'translate_x': i.translation_x,
                'translate_y': i.translation_y,
                'translate_z': i.translation_z,
                'rotate_x': i.rotation_x,
                'rotate_y': i.rotation_y,
                'rotate_z': i.rotation_z,
                'scale_x': i.scale_x,
                'scale_y': i.scale_y,
                'scale_z': i.scale_z,
                'visibility': i.visibility,
                'attr_name': cmds.nodeType(i.get_name())
            })

        return result

    def get_morph_targets(self):
        result = []
        for bs in cmds.ls(type='blendShape'):
            mts = cmds.aliasAttr(bs, q=True)
            if mts:
                for idx, mt in enumerate(mts):
                    if idx % 2 == 0:
                        result.append({
                            'weight': mts[idx + 1],
                            'node_name': cmds.getAttr(f'{bs}.{mts[idx + 1]}'),
                            'parent_name': bs
                        })
        return result

    def get_scene_info(self):
        scene_info = SceneInformation()
        scene_function = CustomSceneFunction()
        return {
            'transforms': scene_info.scene_counter.get_transform_counter().get('transforms'),
            'groups': scene_info.scene_counter.get_transform_counter().get('groups'),
            'empty_groups': len(scene_function.get_empty_groups()),
            'meshes': scene_info.scene_counter.get_poly_counter().get('meshes'),
            'verts': scene_info.scene_counter.get_poly_counter().get('verts'),
            'edges': scene_info.scene_counter.get_poly_counter().get('edges'),
            'faces': scene_info.scene_counter.get_poly_counter().get('faces'),
            'tris': scene_info.scene_counter.get_poly_counter().get('tris'),
            'uvs': scene_info.scene_counter.get_poly_counter().get('uvs'),
            'ngons': scene_info.scene_counter.get_poly_counter().get('ngons'),
            'materials': scene_info.scene_counter.get_material_counter().get('materials'),
            'textures': scene_info.scene_counter.get_texture_counter().get('textures'),
            'cameras': scene_info.scene_counter.get_camera_counter().get('cameras'),
            'joints': scene_info.scene_counter.get_joint_counter().get('joints'),
            'lights': scene_info.scene_counter.get_light_counter().get('lights'),
            'blend_shapes': scene_info.scene_counter.get_blendshape_counter().get('blend_shapes'),
            'morph_targets': scene_info.scene_counter.get_blendshape_counter().get('morph_targets'),
            "nurbs_curves": scene_info.scene_counter.get_nurbscurve_counter().get('nurbs_curve'),
            "root_nodes": scene_info.scene_counter.get_scene_counter().get('root_nodes'),
            "up_axis": scene_info.scene_evaluate.get_settings_evaluate().get('up_axis'),
            "linear": scene_info.scene_evaluate.get_settings_evaluate().get('linear'),
            "angular": scene_info.scene_evaluate.get_settings_evaluate().get('angular'),
            "current_time": scene_info.scene_evaluate.get_settings_evaluate().get('current_time'),
            "anim_start_time": scene_info.scene_evaluate.get_settings_evaluate().get('anim_start_time'),
            "anim_end_time": scene_info.scene_evaluate.get_settings_evaluate().get('anim_end_time'),
            "play_back_start_time": scene_info.scene_evaluate.get_settings_evaluate().get('play_back_start_time'),
            "play_back_end_time": scene_info.scene_evaluate.get_settings_evaluate().get('play_back_end_time'),
            "frame_rate": scene_info.scene_evaluate.get_settings_evaluate().get('frame_rate'),
            'transform_nodes': self.get_transforms(),
            'morph_target_nodes': self.get_morph_targets(),
            'blend_shape_nodes': self.get_blend_shapes(),
        }

    def get_blend_shapes(self):
        result = []
        for i in cmds.ls(type='blendShape'):
            result.append({
                'node_name': i
            })
        return result


class CheckMayaData:
    def __init__(self, file_path: str):
        self.file_path = file_path  # 需要检查的文件路径
        self.fo = CMFileOptions()
        self.fo.set_open_file_options(file_path, o=True, force=True)
        self.scene_file_information = SceneFileInformation(self.fo)

    def get_data(self):
        data = {
            'description': self.scene_file_information.opened_file_status.detail,
            'opened_successfully': self.scene_file_information.opened_file_status.opened_successfully,
            'local_path': self.file_path,
            'scene_info': {},
            # "shape_nodes": [],
        }
        if self.scene_file_information.opened_file_status.opened_successfully:
            data['scene_info'] = self.scene_file_information.get_scene_info()
            # data['transform_nodes'] = self.scene_file_information.get_transforms()
            return data


if __name__ == '__main__':
    file_path = r'D:\svn_project_test\MyDataSVN\trunk\RootFolder\characters\Avatar_Boy_Bow_Gorou\maya.mb'

    md = CheckMayaData(file_path, )

    print(md.get_data())
