import dataclasses
import json
import os
from pprint import pprint

from dc import SVNInfoLocalExtDC, FBXClientConfigDC, RepositoryCustomVerifyDC
from endpoints import Endpoints
from fbx_client.fbx_client_manager import DataManager

from fbx_client.reader import CustomFbxReader
from login import ClientBase
from svn_utils import get_local_file_svn_info, is_svn_repository

root_dir = FBXClientConfigDC.local_svn_path


def get_fbx_paths(root_dir: str):
    result: list[str] = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.fbx'):
                result.append(os.path.join(root, file))
    return result


class FBXClient(ClientBase):
    def __init__(self, config: FBXClientConfigDC):
        super().__init__()
        self.config = config

    def get_fbx_data(self, file_path: str):
        reader = CustomFbxReader()
        reader.load_scene(file_path=file_path)
        data_manager = DataManager(reader.scene)

        svn_info_local = get_local_file_svn_info(file_path)
        svn_info_local_ext = SVNInfoLocalExtDC(
            path=svn_info_local.relative_url,
            revision=svn_info_local.revision,
        )

        data = {
            'repo_data': dataclasses.asdict(self.config.repo),
            'change_file': dataclasses.asdict(svn_info_local_ext),
            'fbx_data': data_manager.get_scene_data(),
            'takes': data_manager.get_takes(),
            'skeletons': [dataclasses.asdict(_) for _ in data_manager.get_skeletons()]
        }
        return data


if __name__ == '__main__':
    # 计算耗时
    import time

    now = time.time()
    config = FBXClientConfigDC(
        RepositoryCustomVerifyDC('MyDataSVN', 'https://QIAOYUANZHEN/svn/MyDataSVN/')
    )
    fbx_client = FBXClient(config)
    fbx_path_list = get_fbx_paths(root_dir)  # [:1]  # TODO:测试1个FBX文件
    for path in fbx_path_list:
        # 判断是否是svn仓库
        if not is_svn_repository(path):
            continue

        data = fbx_client.get_fbx_data(path)
        print(data)
        response = fbx_client.session.post(Endpoints.get_api_url('fbx/receive_fbx_file_data/', print_url=True),
                                           headers=fbx_client.headers, data=json.dumps(data))
        pprint(response.json())

    print(f'耗时:{time.time() - now}')

if __name__ == '__main__1':
    fbx_client = FBXClient()
    fbx_path_list = get_fbx_paths(root_dir)  # [:1]  # TODO:测试1个FBX文件
    d = {
        'repo_name': 'MyDataSVN',
        'file_changes': []
    }
    for path in fbx_path_list:
        svn_info_local = get_local_file_svn_info(path)
        if svn_info_local:
            # print(svn_info_local)
            d['file_changes'].append({
                'path': svn_info_local.relative_url,
                'revision': svn_info_local.revision,
            })
    # response = fbx_client.session.post(Endpoints.get_api_url('fbx/receive_fbx_file_data/', print_url=True),
    #                                    headers=fbx_client.headers, data=json.dumps(d))
    # pprint(response.json())
