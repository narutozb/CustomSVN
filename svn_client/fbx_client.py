import dataclasses
import json
import os

from config import Config
from dc import SVNInfoLocalExtDC
from endpoints import Endpoints
from fbx_client.fbx_client_manager import DataManager

from fbx_client_config import FBXClientConfig

from fbx_client.reader import CustomFbxReader
from login import ClientBase
from svn_utils import get_local_file_svn_info, is_svn_repository

root_dir = FBXClientConfig.local_svn_path


def get_fbx_paths(root_dir: str):
    result: list[str] = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.fbx'):
                result.append(os.path.join(root, file))
    return result


class FBXClient(ClientBase):
    def __init__(self):
        super().__init__()


def get_fbx_data(file_path: str):
    # file_path = fbx_path_list[0]
    reader = CustomFbxReader()
    reader.load_scene(file_path=file_path)
    data_manager = DataManager(reader.scene)

    svn_info_local = get_local_file_svn_info(file_path)
    svn_info_local_ext = SVNInfoLocalExtDC(
        file_path=svn_info_local.url,
        revision=svn_info_local.revision,
        repo_name=Config.REPO_NAME
    )
    data = {
        'change_file': dataclasses.asdict(svn_info_local_ext),
        'fbx_data': data_manager.get_scene_data(),
        'takes': data_manager.get_takes(),
        'skeletons': [dataclasses.asdict(_) for _ in data_manager.get_skeletons()]
    }
    return data


if __name__ == '__main__1':
    # 计算耗时
    import time

    now = time.time()

    fbx_client = FBXClient()
    fbx_path_list = get_fbx_paths(root_dir)  # [:1]  # TODO:测试1个FBX文件
    for path in fbx_path_list:
        # 判断是否是svn仓库
        if not is_svn_repository(path):
            continue

        data = get_fbx_data(path)
        print(data)
        # response = fbx_client.post_data(data=json.dumps(data))

    print(f'耗时:{time.time() - now}')

if __name__ == '__main__':
    fbx_client = FBXClient()
    fbx_path_list = get_fbx_paths(root_dir)  # [:1]  # TODO:测试1个FBX文件
    for path in fbx_path_list[:1]:
        svn_info_local = get_local_file_svn_info(path)
        # print(svn_info_local)
        d = {
            'file_changes': [
                {
                    'path': svn_info_local.relative_url,
                    'revision': svn_info_local.revision,
                    'repo_name': 'MyDataSVN'
                }
            ]
        }
        print(d)

        response = fbx_client.session.post(Endpoints.get_api_url('svn/get_file_change_by_revision/', print_url=True),
                                           headers=fbx_client.headers, data=json.dumps(d))
        print(response.json())
