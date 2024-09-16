import dataclasses
import json

from maya_client import maya_client_manager
from maya_client.local_process import local_process_main
from maya_client.maya_data import MayaData
from settings import MayaClientSettings

if __name__ == '__main__2':
    client = maya_client_manager.MayaClientManager()
    d = {
        "repository_name": "MyDataSVN",
        "commit_revision": 8,
        "path": "/trunk/RootFolder/_test_file3.mb",
        "opened_successfully": True,
        "status": "update",
        "description": "sdaff",
        "local_path": None,
        "client_version": None
    }
    md = MayaData()

    # print(md.get_data())
    # md.get_data()
    r = client.session.post('http://127.0.0.1:8000/api/maya/mayafile/command/',
                            headers=client.headers, data=json.dumps(d))
    print(r.text)
    # client.auto_send_changed_files_data()

if __name__ == '__main__':

    # results = local_process_main()
    for repo_path in MayaClientSettings.get_local_svn_repo_path():
        print(repo_path)
        client = maya_client_manager.MayaClientManager(repo_path, update_to_revision=3)

        latest_commit = client.get_latest_commit()


        for revision in range(1, latest_commit.revision+1):
            client = maya_client_manager.MayaClientManager(repo_path, update_to_revision=revision)
            r = client.get_file_changes_from_custom_server(revision=revision)
            print(r)
            client.send_data()

    # for i in results:
    #     r = client.session.post('http://127.0.0.1:8000/api/maya/mayafile/command/',
    #                             headers=client.headers, data=json.dumps(i))
    #     print(r.text)
