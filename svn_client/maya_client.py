import os

os.environ['LC_ALL'] = 'en_US.UTF-8'

from maya_client import maya_client_manager

if __name__ == '__main__':
    client = maya_client_manager.MayaClientManager()

    client.auto_send_changed_files_data()
