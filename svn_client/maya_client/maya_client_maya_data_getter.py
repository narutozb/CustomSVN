import os
import subprocess

from classes import SVNFileSimpleDC
from config import Config
from maya_client_config import MayaClientConfig


def parse_svn_info(info_text):
    info = {}
    for line in info_text.splitlines():
        if ': ' in line:
            key, value = line.split(': ', 1)
            info[key.strip()] = value.strip()
    return info


def get_svn_info(directory):
    # 存储文件版本信息的列表
    file_info_list = []

    # 遍历指定目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # Skip files in IGNORED_PATHS
            if any(ignored_path in file_path for ignored_path in Config.IGNORED_PATHS):
                continue
            try:
                # Check if the file is under SVN management
                svn_status_result = subprocess.run(['svn', 'status', '--no-ignore', file_path], capture_output=True,
                                                   text=True)
                if svn_status_result.stdout.startswith('?'):
                    print(f"File {file_path} is not under SVN management. Skipping...")
                    continue

                # 执行 svn info 命令
                result = subprocess.run(['svn', 'info', file_path], capture_output=True, text=True, check=True)
                # 解析输出
                info = parse_svn_info(result.stdout)
                file_info_list.append(info)
            except subprocess.CalledProcessError as e:
                print(f"Error executing svn info on {file_path}: {e}")

    return file_info_list


class MayaDataGetter:
    def __init__(self):
        pass

    @classmethod
    def get_svn_file_path(cls, svn_url, local_dir):
        try:
            # 使用svn命令查看文件路径
            result = subprocess.run(['svn', 'info', svn_url], capture_output=True, text=True, check=True)

            # 提取文件路径
            file_info = result.stdout
            file_path = ""
            for line in file_info.split('\n'):
                if line.startswith('Path:'):
                    file_path = line.split(': ')[1]
                    break

            # 组合本地文件路径
            local_file_path = f"{local_dir}/{file_path}"

            return local_file_path

        except subprocess.CalledProcessError as e:
            print(f"Error running svn command: {e}")
            return None

    @classmethod
    def get_local_changed_files(cls):
        result = []
        for i in get_svn_info(MayaClientConfig.local_svn_path):
            # 判断文件后缀是否与MayaClientConfig.MAYA_FILE_SUFFIXES中的任意一个匹配
            if any(i.get('Path').endswith(suffix) for suffix in MayaClientConfig.MAYA_FILE_SUFFIXES):
                latest_changed_rev = int(i.get('Last Changed Rev'))
                result.append(
                    SVNFileSimpleDC(local_path=i.get('Path'), url=i.get('URL'), revision=latest_changed_rev))
        return result
