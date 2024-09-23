import dataclasses
import json

from maya_client import maya_client_manager
from settings import MayaClientSettings

if __name__ == '__main__':

    # while True:
    for repo_path_setting in MayaClientSettings.get_local_svn_repo_path():
        client = maya_client_manager.MayaClientManager(repo_path_setting)
        latest_commit = client.get_latest_commit()
        client.run_update_from_earliest_commit_without_mayafile()
