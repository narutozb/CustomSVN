import dataclasses
import subprocess
import os


class SvnInfo:
    def __init__(self, svn_info: dict):
        self.path = svn_info.get('Path')
        self.URL = svn_info.get('URL')
        self.Relative_URL = svn_info.get('Relative URL')
        self.Repository_Root = svn_info.get('Repository Root')
        self.Repository_UUID = svn_info.get('Repository UUID')
        self.Revision = svn_info.get('Revision')
        self.Node_kind = svn_info.get('Node Kind')
        self.Schedule = svn_info.get('Schedule')
        self.Last_Changed_Author = svn_info.get('Last Changed Author')
        self.Last_Changed_Rev = svn_info.get('Last Changed Rev')
        self.Last_Changed_Date = svn_info.get('Last Changed Date')
        self.Text_Last_Updated = svn_info.get('Text Last Updated')

    def get_local_full_path(self):
        return os.path.join(local_svn_path, self.path)


def run_svn_command(command, cwd):
    """Run a given SVN command in the specified working directory."""
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout


def get_svn_list(path):
    """Get a list of files and directories in the SVN repository."""
    command = ["svn", "list", "--recursive"]
    return run_svn_command(command, cwd=path).splitlines()


def get_svn_info(path, target):
    """Get the SVN info for a specific file or directory."""
    command = ["svn", "info", target]
    info_output = run_svn_command(command, cwd=path)
    info = {}
    for line in info_output.splitlines():
        key, _, value = line.partition(": ")
        if key and value:
            info[key.strip()] = value.strip()
    return info


def _get_svn_file_info(svn_path):
    """
    获取指定路径下的所有文件的SVN信息
    返回结果示例：
    
    [
    ('RootFolder/', {'Path': 'RootFolder', 'Working Copy Root Path': 'D:\\test_svn', 'URL': 'https://reponame/svn/TestRepo/RootFolder', 'Relative URL': '^/RootFolder', 'Repository Root': 'https://reponame/svn/TestRepo', 'Repository UUID': '9741170c-bef4-f749-ac4b-0fd2de7c555f', 'Revision': '4', 'Node Kind': 'directory', 'Schedule': 'normal', 'Last Changed Author': 'qyz', 'Last Changed Rev': '4', 'Last Changed Date': '2023-05-06 00:27:03 +0900 (周六, 06 5月 2023)'}),
    ('RootFolder/test_doc.docx', {'Path': 'RootFolder\\test_doc.docx', 'Name': 'test_doc.docx', 'Working Copy Root Path': 'D:\\test_svn', 'URL': 'https://reponame/svn/TestRepo/RootFolder/test_doc.docx', 'Relative URL': '^/RootFolder/test_doc.docx', 'Repository Root': 'https://reponame/svn/TestRepo', 'Repository UUID': '9741170c-bef4-f749-ac4b-0fd2de7c555f', 'Revision': '4', 'Node Kind': 'file', 'Schedule': 'normal', 'Last Changed Author': 'qyz', 'Last Changed Rev': '4', 'Last Changed Date': '2023-05-06 00:27:03 +0900 (周六, 06 5月 2023)', 'Text Last Updated': '2024-05-11 00:59:53 +0900 (周六, 11 5月 2024)', 'Checksum': '7e8495934c80184e4aea2ac43cf19a5b7a6a3cdb'})
    ]
    
    """
    try:
        files_and_dirs = get_svn_list(svn_path)
        all_info = []
        for item in files_and_dirs:
            info = get_svn_info(svn_path, item)
            all_info.append((item, info))
        return all_info
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running SVN command: {e}")
        return []


def get_svn_file_info(svn_path):
    """
    获取指定路径下的所有文件的SVN信息
    """
    return [(SvnInfo(_[1])) for _ in _get_svn_file_info(svn_path)]


if __name__ == "__main__":
    # 设置本地SVN下载仓库的保存路径
    local_svn_path = r"D:\test_svn"
    # 获取所有文件的信息
    svn_file_info_list = _get_svn_file_info(local_svn_path)
    for file_info in svn_file_info_list:
        print(file_info)
        # print(f"File: {file_info[0]}")
        # for key, value in file_info[1].items():
        #     print(f"  {key}: {value}")
        # print()
