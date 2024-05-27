import requests

from config import Config
from svn_utils import get_token


class MayaClientManager:
    def __init__(self):
        self.session = requests.Session()
        self.token = get_token(self.session, Config.USERNAME, Config.PASSWORD, Config.API_URL)
        if not self.token:
            raise Exception("Failed to get token")
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }

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

client = MayaClientManager()
sended_data = client.send_scene_info(scene_info_data)
print(sended_data.content)
# print(client.session.get(f'{Config.ROOT_URL}/api/repositories/', headers=client.headers).content)

'http://127.0.0.1:8000/api/repositories/'
