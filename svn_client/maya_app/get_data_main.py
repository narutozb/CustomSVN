import base64
import json
import os.path
import sys
import uuid
import tempfile

from custom_maya.custom_maya_class.scene_property import CMFileOptions
from custom_maya.custom_maya_class.scenefile_application import CMApplication

from maya_standalone.scene_data import CheckMayaData, CustomCMApplication, SceneFileInformation


def decode_arg(encoded_arg):
    # 使用base64解码并重新编码为utf-8
    return base64.b64decode(encoded_arg).decode('utf-8')


class Checker:
    def __init__(self, file_list):
        results = []
        md = CheckMayaData(maya_file_path, )
        maya_file_list: list = file_list


if __name__ == '__main__':
    # print(sys.argv)
    maya_file_path = decode_arg(sys.argv[1])
    print(f'{maya_file_path}')
    with open(maya_file_path, 'r', encoding='utf8') as f:
        maya_file_list = json.loads(f.read())

    result: list = []
    for file_path in maya_file_list:
        # fo.set_open_file_options(file_path, o=True, force=True)
        # scene = SceneFileInformation(fo)
        # print(scene.get_data())
        md = CheckMayaData(file_path, )
        d = {
            "opened_successfully": md.scene_file_information.opened_file_status.opened_successfully,
            "description": md.scene_file_information.opened_file_status.detail,
            'local_path': file_path,
        }
        result.append(d)

    data_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}.json')
    with open(data_path, 'w', encoding='utf8') as f:
        f.write(json.dumps(result))
        print(f'MAYAAPP_RESULT:{data_path}')
