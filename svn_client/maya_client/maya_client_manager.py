from config import Config
from endpoints import Endpoints
from login import ClientBase
import maya_client_config


class MayaClientManager(ClientBase):

    def __init__(self):
        super().__init__()

    def get_maya_changed_maya_files(self, local_current_revision: int):
        '''
        获取必要的需要将数据上传的文件信息
        :return:
        '''
        return self.session.get(Endpoints.get_maya_file_changes_by_repo_and_revision_api_url(
            Config.REPO_NAME,
            local_current_revision,
            maya_client_config.MayaClientConfig.version
        ), headers=self.headers)
