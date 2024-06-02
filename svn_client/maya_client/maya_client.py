import json

import maya_client_config
import maya_client_manager
import maya_data

from classes import SVNChangedFileDC
from maya_client_maya_data_getter import MayaDataGetter
from svn_utils import get_local_last_changed_revision

if __name__ == '__main__':
    client = maya_client_manager.MayaClientManager()

    local_last_changed_rev = int(get_local_last_changed_revision(maya_client_config.MayaClientConfig.local_svn_path))

    response = client.get_maya_changed_maya_files(local_last_changed_rev)
    print('results')
    print(response.json().get('results'))
    if response.json().get('results'):
        results = [SVNChangedFileDC(
            revision=local_last_changed_rev,
            change_type=_.get('change_type'),
            url=_.get('file_path'),
            change_file_id=_.get('id')
        ) for _ in response.json().get('results')]

        maya_data_getter = MayaDataGetter()
        local_svn_files = maya_data_getter.get_local_changed_files()

        # 获取自定义svn服务器非同步文件。也就是需要上传数据的文件
        file_path_list: [SVNChangedFileDC] = []
        for i in results:
            if i in local_svn_files:
                file_path_list.append(i)

        for i in file_path_list:
            print(i)
            md = maya_data.CheckMayaData(i.local_path, i.change_file_id)
            data = md.get_data()
            url = r'http://127.0.0.1:8000/api/maya/mayafilesview/'

            ps = client.session.post(url, data=json.dumps(data), headers=client.headers)
            print(ps.json())
