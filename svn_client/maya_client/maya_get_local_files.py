import subprocess
import os

import maya_client_config

def get_svn_info(directory):
    # 存储文件版本信息的列表
    file_info_list = []

    # 遍历指定目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                # 执行 svn info 命令
                result = subprocess.run(['svn', 'info', file_path], capture_output=True, text=True, check=True)
                # 解析输出
                info = parse_svn_info(result.stdout)
                file_info_list.append(info)
            except subprocess.CalledProcessError as e:
                print(f"Error executing svn info on {file_path}: {e}")

    return file_info_list


def parse_svn_info(info_text):
    info = {}
    for line in info_text.splitlines():
        if ': ' in line:
            key, value = line.split(': ', 1)
            info[key.strip()] = value.strip()
    return info


def print_svn_info(file_info_list):
    for info in file_info_list:
        print("File:", info.get("Path"))
        print("  URL:", info.get("URL"))
        print("  Revision:", info.get("Revision"))
        print("  Last Changed Author:", info.get("Last Changed Author"))
        print("  Last Changed Rev:", info.get("Last Changed Rev"))
        print("  Last Changed Date:", info.get("Last Changed Date"))
        print()


if __name__ == "__main__":

    directory = maya_client_config.MayaClientPaths.local_svn_path # 替换为你的SVN检出路径
    file_info_list = get_svn_info(directory)
    print_svn_info(file_info_list)
