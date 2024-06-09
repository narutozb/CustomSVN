import subprocess

# # 设置命令行代码页为 437
# subprocess.run('chcp 437', shell=True)

from maya_client import maya_client_manager

if __name__ == '__main__':
    client = maya_client_manager.MayaClientManager()

    client.auto_send_changed_files_data()
