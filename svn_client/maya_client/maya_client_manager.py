import json
import os.path
import tempfile
import uuid
from collections import namedtuple

from config import Config
from svn_client.dc import RepoPathSettings, FileChangeFromServerDC
from apis.client_base import ClientBase
from maya_client.local_process import LocalSVNUtilities
from maya_client.maya_data import MayaData
from svn_client.svn_utils import get_local_file_svn_info


class MayaClientManager(ClientBase):

    def __init__(self, repo_path_settings: RepoPathSettings, update_to_revision: int = None):
        super().__init__()
        self.update_to_revision = update_to_revision
        self.repo_path_settings = repo_path_settings
        self.repository = self.get_repository(self.repo_path_settings.REPO_NAME)
        self.local_svn_utilities = LocalSVNUtilities()

    # def update_to_revision(self):

    def send_data(self):

        data: list = []
        # 1.1 更新特定本地仓库到特定revision
        for path in self.repo_path_settings.LOCAL_SVN_REPO_PATH_LIST:

            self.local_svn_utilities.update_to_revision(self.update_to_revision, path)

            # 1.2. 获取本地svn管理的maya文件列表和svn基本信息
            maya_file_list = self.local_svn_utilities.get_maya_file_list(path)
            pre_list = []
            for maya_file_path in maya_file_list:
                mf = get_local_file_svn_info(maya_file_path)
                if mf.last_change_rev == self.update_to_revision:
                    pre_list.append(maya_file_path)

            data_from_maya = self.get_data_from_maya(pre_list)
            send_data = {'maya_files': data_from_maya}
            for i in data_from_maya:
                print(i)

            # r = self.session.post('http://127.0.0.1:8000/api/maya/mayafile/command/',
            #                       headers=self.headers, data=json.dumps(send_data))
            # print(r.text)

        # 2. 在自定义服务器中查询是否存在maya文件信息。筛选需要上传或者更新的文件列表

        # 3. 将数据传入maya获取必要数据。然后获取

        # 4. 将必要数据传输到自定义服务器进行储存

    def get_data_from_maya(self, maya_file_path):
        result = []
        if not maya_file_path:
            return result

        save_maya_file_list_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}.json')
        with open(save_maya_file_list_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(maya_file_path))
        print(save_maya_file_list_path)

        md = MayaData()
        data_from_maya = md.get_data(save_maya_file_list_path)

        for data in data_from_maya:
            local_path = data['local_path']
            file_info = get_local_file_svn_info(local_path)
            data.update({
                'repository_name': self.repo_path_settings.REPO_NAME,
                'commit_revision': file_info.last_change_rev,
                'path': file_info.relative_url
            })
            result.append(data)

        return result

    def get_file_changes_from_custom_server(self, revision: int = None):

        repository_id = self.repository.id
        params = {'repository_id': repository_id, 'revision': revision}
        commit_response = self.session.get(f'{Config.ROOT_URL}/api/svn/commits_query/', params=params
                                           )
        commit_id = commit_response.json().get('results')
        if commit_id:
            commit_id = commit_id[0].get('id')

        file_changes_response = self.session.get(
            f'{Config.ROOT_URL}/api/svn/commits_query/{commit_id}/file_changes/',
            params={'suffix': ['ma', 'mb'], 'action': ['A', 'M'], 'kind': 'file'}
        )
        result: list[FileChangeFromServerDC] = []
        for i in file_changes_response.json().get('results'):
            fc = FileChangeFromServerDC(
                *[i.get(_) for _ in ['id', 'commit', 'path', 'action']]
            )
            result.append(fc)
        return result

    def get_latest_commit(self):
        __fields = ['id', 'revision', 'branch', 'message', 'author', 'date']
        __Commit = namedtuple('__Commit', __fields)

        params = {'repository_id': self.repository.id}
        response = self.session.get(f'{Config.ROOT_URL}/api/svn/commits_query/latest_commit/',
                                    params=params).json()

        if response:
            return __Commit(**response)

    def get_repository(self, repo_name: str):
        RepositoryAPI = namedtuple('RepositoryAPI', ['id', 'name', 'url', 'description'])
        data = self.session.get(f'{Config.ROOT_URL}/api/svn/repositories_query/',
                                params={'name': repo_name}).json().get('results')
        if data:
            return RepositoryAPI(**data[0])
