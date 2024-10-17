import json
import os.path
import tempfile
import uuid
from collections import namedtuple

from apis import SvnApis
from apis.maya_apis import MayaApis
from config import Config
from svn_client.dc import RepoPathSettings, FileChangeFromServerDC, QueryRepositoriesFilter, QueryBranchesFilter, \
    BranchQueryS, CommitQueryS
from apis.client_base import ClientBase
from maya_client.local_process import LocalSVNUtilities
from maya_client.maya_data import MayaData
from svn_client.svn_utils import get_local_file_svn_info, get_svn_branch_path


class MayaClientManager(ClientBase):

    def __init__(self, repo_path_settings: RepoPathSettings):
        super().__init__()
        self.repo_path_settings = repo_path_settings
        self.repository = self.get_repository(self.repo_path_settings.REPO_NAME)
        self.local_svn_utilities = LocalSVNUtilities()
        self.svn_apis = SvnApis(self)
        self.maya_apis = MayaApis(self)

    def send_data(self, update_to_revision: int):
        # 1.1 更新特定本地仓库到特定revision
        for path in self.repo_path_settings.LOCAL_SVN_REPO_PATH_LIST:
            # 1.1.1 将本地仓库升级到特定revision
            if not update_to_revision:
                '''
                当revision为None时，不更新本地仓库
                '''
                continue

            self.local_svn_utilities.update_to_revision(update_to_revision, path)

            # 1.2. 获取本地svn管理的maya文件列表和svn基本信息
            maya_file_list = self.local_svn_utilities.get_maya_file_list(path)
            pre_list = []  # 获取需要上传的文件列表
            for maya_file_path in maya_file_list:
                mf = get_local_file_svn_info(maya_file_path)
                if mf.last_change_rev == update_to_revision:
                    pre_list.append(maya_file_path)

            data_from_maya = self.get_data_from_maya(pre_list)

            send_data = {
                'maya_files': data_from_maya,
            }

            # 如果有数据，就发送数据
            if data_from_maya:
                r = self.session.post('http://127.0.0.1:8000/api/maya/mayafile/save_data/',
                                      headers=self.headers, data=json.dumps(send_data))

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
        commit_response = self.session.get(f'{Config.ROOT_URL}/api/svn/commits_query/', params=params)
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
        response = self.session.get(f'{Config.ROOT_URL}/api/svn/repositories_query/{self.repository.id}/latest_commit/',
                                    ).json()
        if response:
            return __Commit(**response)

    def get_repository(self, repo_name: str):

        RepositoryAPI = namedtuple('RepositoryAPI', ['id', 'name', 'url', 'created_at', 'description'])

        data = self.session.get(f'{Config.ROOT_URL}/api/svn/repositories_query/',
                                params={'name': repo_name}).json().get('results')
        if data:
            return RepositoryAPI(**data[0])

    def get_prepare_process_revision(self, local_path: str):
        '''
        获取commit考前的不存在MayaFile的Commit数据。为更新本地仓库和之后的上传数据做准备的函数
        :param local_path:
        :return:
        '''
        branch_name = get_svn_branch_path(local_path)
        branches = self.svn_apis.get_branches(QueryBranchesFilter(name=branch_name, repo_id=self.repository.id)).get(
            'results')

        branch_id = BranchQueryS(**branches[0]).id
        earliest_commit_without_mayafile = self.maya_apis.get_earliest_commit_without_mayafile(
            {'branch_id': branch_id})

        return CommitQueryS(**earliest_commit_without_mayafile)

    def run_update_from_earliest_commit_without_mayafile(self, ):

        '''
        更新流程如下
        1. 通过branch_id获取

        :return:
        '''
        for path in self.repo_path_settings.LOCAL_SVN_REPO_PATH_LIST:
            prepare_process_revision = self.get_prepare_process_revision(path)
            send_data_response = self.send_data(prepare_process_revision.revision)
            print(send_data_response)
