from dataclasses import dataclass
from pprint import pprint

from custom_maya.custom_maya_class.scene_property import CMFileOptions
from custom_maya.custom_maya_class.scenefile_application import CMApplication, CustomSceneFunction
from custom_maya.tools.custom_maya_client.scene_utilities import SceneInformation

from maya_client_config import MayaClientConfig


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


class SceneFileInformation:
    def __init__(self, open_file_option: CMFileOptions):
        self.app = CMApplication()
        self.open_file_option = open_file_option
        self.opened_file_status = self.open_scene_file()

    def open_scene_file(self) -> FileOpenStatus:
        open_file_options = self.open_file_option.get_open_file_options()
        file_path = open_file_options[0][0]
        try:
            self.app.open_file(self.open_file_option)

        except RuntimeError as e:
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
        }


class CheckMayaData:
    def __init__(self, file_path: str, changed_file: str | int):
        self.changed_file = changed_file  # url of the changed file
        self.file_path = file_path  # 需要检查的文件路径
        self.fo = CMFileOptions()
        self.fo.set_open_file_options(file_path, o=True, force=True)
        self.scene_file_information = SceneFileInformation(self.fo)

    def get_data(self):
        data = {
            'description': self.scene_file_information.opened_file_status.detail,
            'changed_file': self.changed_file,
            'opened_successfully': self.scene_file_information.opened_file_status.opened_successfully,
            'local_path': self.file_path,
            'client_version': MayaClientConfig.version,
            'scene_info': {},
            "transform_nodes": [],
            "shape_nodes": [],
        }
        if self.scene_file_information.opened_file_status.opened_successfully:
            data['scene_info'] = self.scene_file_information.get_scene_info()

        return data


if __name__ == '__main__':
    file_path = r'D:\svn_project_test\MyDataSVN\RootFolder\_test_file.mb'

    md = CheckMayaData(file_path, 'dummy')
    pprint(md.get_data())
