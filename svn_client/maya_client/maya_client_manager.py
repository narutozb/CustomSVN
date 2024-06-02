import locale

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

import json
import subprocess

from classes import SVNChangedFileDC
from config import Config
from endpoints import Endpoints
from login import ClientBase
import maya_client_config
from maya_client.maya_client_utils import MayaDataGetter
from maya_client.maya_standalone.scene_data import CheckMayaData
from svn_utils import get_local_last_changed_revision


class MayaClientManager(ClientBase):

    def __init__(self):
        super().__init__()

    def get_changed_maya_files(self, local_current_revision: int):
        '''
        获取必要的需要将数据上传的文件信息
        :return:
        '''
        return self.session.get(Endpoints.get_maya_file_changes_by_repo_and_revision_api_url(
            Config.REPO_NAME,
            local_current_revision,
            maya_client_config.MayaClientConfig.version
        ), headers=self.headers)

    def get_diff_local_maya_files(self, ):
        local_last_changed_rev = int(
            get_local_last_changed_revision(maya_client_config.MayaClientConfig.local_svn_path))
        response = self.get_changed_maya_files(local_last_changed_rev)
        if response.json().get('results'):
            results = [SVNChangedFileDC(
                revision=local_last_changed_rev,
                change_type=_.get('change_type'),
                url=_.get('file_path'),
                change_file_id=_.get('id'),

            ) for _ in response.json().get('results')]
        else:
            results = []

        maya_data_getter = MayaDataGetter()
        local_svn_files = maya_data_getter.get_local_changed_files()

        diff_changed_maya_files: [SVNChangedFileDC] = []
        for i in results:
            print(i)
            for j in local_svn_files:
                if i.url == j.url:
                    i.local_path = j.local_path
                    diff_changed_maya_files.append(i)
                    continue

        return diff_changed_maya_files

    def send_changed_maya_files_data_to_custom_server(self):
        changed_files = self.get_diff_local_maya_files()
        for i in changed_files:
            md = CheckMayaData(i.local_path, i.change_file_id)
            data = md.get_data()
            url = Endpoints.get_api_url(Endpoints.maya_sceneinfos)
            ps = self.session.post(url, data=json.dumps(data), headers=self.headers)
            print(ps.json())

    def auto_send_changed_files_data(self):
        # Step 1: Get the latest revision from the custom server
        response = self.session.get(Endpoints.get_latest_revision_api_url(Config.REPO_NAME), headers=self.headers)
        latest_server_revision = response.json().get('latest_revision')

        # Step 2: Check if the local repository's revision is older than the server's
        local_last_changed_rev = int(
            get_local_last_changed_revision(maya_client_config.MayaClientConfig.local_svn_path))

        if local_last_changed_rev < latest_server_revision:
            # Step 3: Update the local repository and send the changed_file data to the server for each new revision
            for revision in range(local_last_changed_rev + 1, latest_server_revision + 1):
                # Update to the specific revision
                subprocess.run(
                    ['svn', 'update', '-r', str(revision), maya_client_config.MayaClientConfig.local_svn_path],
                    check=True, universal_newlines=True)

                # Send the changed_file data to the server
                changed_files = self.get_diff_local_maya_files()
                print(changed_files)
                # print(changed_files)
                for i in changed_files:
                    md = CheckMayaData(i.local_path, i.change_file_id)
                    data = md.get_data()
                    print(data)
                    url = Endpoints.get_api_url(Endpoints.maya_sceneinfos)
                    response = self.session.post(url, data=json.dumps(data), headers=self.headers)
                    print(response.json())
