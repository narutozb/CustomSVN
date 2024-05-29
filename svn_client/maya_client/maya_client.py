import os.path

import maya_client_config
import maya_client_manager
from classes import SVNChangedFileDC
from maya_client_config import MayaClientPaths
from maya_client_maya_data_getter import MayaDataGetter
from temp import get_local_current_revision

scene_info_data = {
    "transforms": 10,
    "groups": 5,
    "empty_groups": 2,
    "meshes": 3,
    "verts": 1000,
    "edges": 2000,
    "faces": 1500,
    "tris": 3000,
    "uvs": 400,
    "ngons": 0,
    "materials": 10,
    "textures": 15,
    "cameras": 2,
    "joints": 8,
    "lights": 4,
    "blend_shapes": 0,
    "morph_targets": 1,
    "nurbs_curves": 3,
    "root_nodes": 1,
    "up_axis": "Y",
    "linear": "cm",
    "angular": "deg",
    "current_time": 24.0,
    "anim_start_time": 0.0,
    "anim_end_time": 100.0,
    "play_back_start_time": 0.0,
    "play_back_end_time": 100.0,
    "frame_rate": 24.0

}

if __name__ == '__main__':
    client = maya_client_manager.MayaClientManager()
    local_current_revision = int(get_local_current_revision(maya_client_config.MayaClientPaths.local_svn_path))
    response = client.get_maya_changed_maya_files(local_current_revision)
    results = [SVNChangedFileDC(
        revision=local_current_revision,
        change_type=_.get('change_type'),
        url=_.get('file_path'),
    ) for _ in response.json().get('results')]
    maya_data_getter = MayaDataGetter()
    local_svn_files = maya_data_getter.get_local_changed_files()

    for i in local_svn_files:
        if i in results:
            print(i)



    # for i in results:
    #     local_path = maya_data_getter.get_svn_file_path(i.file_path, MayaClientPaths.local_svn_path)
    #     msg = f'路径{local_path}'
    #     if os.path.exists(local_path):
    #         msg += '存在'
    #     else:
    #         msg += '不存在'
    #
    #     print(msg)
