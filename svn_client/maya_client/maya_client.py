import requests

from config import Config
from endpoints import Endpoints
from login import ClientBase
from temp import get_local_current_revision
from maya_client_paths import MayaClientPaths


class MayaClientManager(ClientBase):
    def __init__(self):
        super().__init__()

    def send_scene_info(self, data: dict):
        url = f'{Config.ROOT_URL}/api/maya/sceneinfos/'
        response = requests.post(url, json=scene_info_data, headers=self.headers)

        return response


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
    client = MayaClientManager()
    # sended_data = client.send_scene_info(scene_info_data)
    # print(sended_data.content)

    local_current_revision = get_local_current_revision(MayaClientPaths.local_svn_path)

    response = client.session.get(
        Endpoints.get_file_changes_by_repo_and_revision_api_url('TestRepo', int(local_current_revision)),
        headers=client.headers
    )
    results = response.json().get('results')
    print(results)

    '''
    /api/svn/repositories/TestRepo/commits/26/file_changes/
    /api/svn/repositories/TestRepo/commits/26/file_changes/
    '''
