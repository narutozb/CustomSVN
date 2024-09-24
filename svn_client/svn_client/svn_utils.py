# svn_utils.py

import subprocess
import sys
import json
import logging
from typing import List, Optional
from urllib.parse import unquote
import xml.etree.ElementTree as ET

from config import SUBPROCESS_ENV
from svn_client.dc import SVNInfoLocalDC, CommitLogDC, FileChangeDC
from svn_client.exceptions import SVNUpdateError

logger = logging.getLogger(__name__)


def get_svn_log2(repo_url: str, start_revision: int = 1, end_revision: Optional[int] = None) -> str:
    if not end_revision:
        end_revision = 'HEAD'

    cmd = ['svn', 'log', repo_url, '--verbose', '--xml', '-r', f'{start_revision}:{end_revision}']
    logger.debug(f'执行命令: {" ".join(cmd)}')

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=SUBPROCESS_ENV, check=True)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logger.error(f'SVN log 命令执行错误: {e.stderr.decode()}')
        raise


def parse_svn_log2(xml_data: str) -> List[CommitLogDC]:
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        logger.error(f'解析 XML 数据出错: {e}')
        raise

    commits: List[CommitLogDC] = []
    for entry in root.findall('logentry'):
        # 提取数据并进行错误处理
        try:
            revision = int(entry.get('revision'))
            author = entry.findtext('author')
            date = entry.findtext('date')
            msg = entry.findtext('msg')
            paths = entry.find('paths')
            file_changes = [
                FileChangeDC(
                    path=path_elem.text,
                    action=path_elem.get('action'),
                    kind=path_elem.get('kind')
                )
                for path_elem in paths
            ] if paths else []
            branch_name = get_commit_branch_name(file_changes[0].path) if file_changes else 'unknown'
            commit = CommitLogDC(
                revision=revision,
                author=author,
                date=date,
                message=msg,
                branch_name=branch_name,
                file_changes=file_changes
            )
            commits.append(commit)
        except Exception as e:
            logger.error(f'处理日志条目时出错: {e}')
            continue

    return commits


def __get_svn_changes(repo_url, revisions):
    all_changes = {}
    for revision in revisions:
        result = subprocess.run(['svn', 'diff', repo_url, '-c', str(revision), '--summarize'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=SUBPROCESS_ENV)
        changes = []
        for line in handle_encoding(result.stdout).splitlines():
            change_type, file_path = line.split()[:2]
            changes.append({'file_path': unquote(file_path), 'change_type': change_type})
        all_changes[revision] = changes
    return all_changes


def handle_encoding(output):
    encodings = ['utf-8', 'shift_jis', 'gbk', 'cp1256']  # 常见的编码列表，可根据需要添加
    for encoding in encodings:
        try:
            return output.decode(encoding)
        except UnicodeDecodeError:
            continue
    return output.decode('utf-8', errors='ignore')


def run_svn_command(command, cwd):
    """Run a given SVN command in the specified working directory."""
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True, env=SUBPROCESS_ENV)
    return result.stdout


def get_local_current_revision(svn_path):
    """Get the current revision of the SVN repository."""
    command = ["svn", "info"]
    info_output = run_svn_command(command, cwd=svn_path)
    for line in info_output.splitlines():
        if line.startswith("Revision:"):
            return line.split()[1]
    return None


def get_local_last_changed_revision(svn_path):
    """Get the current revision of the SVN repository."""
    command = ["svn", "info"]
    info_output = run_svn_command(command, cwd=svn_path)
    for line in info_output.splitlines():
        print(line)
        if line.startswith("Last Changed Rev:"):
            return line.split()[-1]
    return None


def get_local_file_svn_info(local_path: str, print_command=False):
    '''
    获取本地特定地址的信息
    :param local_path:
    :param print_command:
    :return:
    '''
    commands = ['svn', 'info', local_path]
    if print_command:
        print(' '.join(commands))

    try:
        result = subprocess.run(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, check=True, env=SUBPROCESS_ENV)
    except Exception as e:
        return None

    svn_info = SVNInfoLocalDC()
    for line in result.stdout.splitlines():
        if line.startswith('URL:'):
            svn_info.url = line.split()[1]
        if line.startswith('Revision:'):
            svn_info.revision = int(line.split()[1])
        if line.startswith('Node Kind:'):
            svn_info.node_kind = line.split()[-1]
        if line.startswith('Schedule:'):
            svn_info.schedule = line.split()[-1]
        if line.startswith('Last Changed Author:'):
            svn_info.last_changed_author = line.split()[-1]
        if line.startswith('Last Changed Rev:'):
            svn_info.last_change_rev = int(line.split()[-1])
        if line.startswith('Last Changed Date:'):
            svn_info.last_changed_date = line.split(':', 1)[1].strip()
        if line.startswith('Relative URL'):
            svn_info.relative_url = unquote(line.split(':', 1)[1].strip().replace('^', '', 1))

    return svn_info


def is_svn_repository(path):
    '''
    检查指定路径是否是svn仓库
    :param path:
    :return:
    '''
    result = subprocess.run(['svn', 'info', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=SUBPROCESS_ENV)
    return result.returncode == 0


def update_to_revision(revision, repo_path):
    try:
        subprocess.run(
            ['svn', 'update', '-r', str(revision), repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=SUBPROCESS_ENV,
        )
        print(f'更新成功!仓库{repo_path}到revision:{revision}')
    except subprocess.CalledProcessError as e:
        raise SVNUpdateError(f'更新失败!!在将repo_path:{repo_path}更新到revision:{revision}时出现了异常')


def cleanup(repo_path):
    try:
        subprocess.run(
            ['svn', 'cleanup', repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=SUBPROCESS_ENV,
        )
    except subprocess.CalledProcessError as e:
        raise SVNUpdateError(f'cleanup失败!!')


def list_svn_files(repo_path):
    """
    获取指定路径下被SVN管理的文件列表。

    :param repo_path: 本地SVN仓库路径
    :return: 被SVN管理的文件列表
    """
    try:
        result = subprocess.run(
            ["svn", "list", "--recursive", repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        files = result.stdout.splitlines()
        return files
    except subprocess.CalledProcessError as e:
        print(f"获取文件列表失败: {e.stderr}")
        return []


def get_latest_svn_revision(repo_url):
    '''
    获取svn服务器最后的revision
    :param repo_url:
    :return:
    '''
    commands = ['svn', 'info', '--show-item', 'revision', repo_url]
    result = subprocess.run(commands, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=SUBPROCESS_ENV)

    if result.stdout.strip():
        return int(result.stdout.strip())
    else:
        print("Error: SVN command did not return a result.")
        return None


def calculate_size(data):
    return sys.getsizeof(json.dumps(data))


def get_commit_branch_name(path, standard_dirs=None):
    """
    从给定的相对路径中提取 SVN 分支名称。

    参数：
    - path: SVN 仓库的相对路径（以 '/' 开头）

    返回值：
    - branch_name: 提取的分支名称（如 'trunk'、'branches/release1.1'、'tags/0.8.1'）

    示例：
    - '/trunk/test/unit/lib/redmine/hook_test.rb' -> 'trunk'
    - '/trunk/app/controllers/settings_controller.rb' -> 'trunk'
    - '/sandbox/rails-2.2/app/helpers/application_helper.rb' -> 'sandbox/rails-2.2'
    - '/tags/0.8.1' -> 'tags/0.8.1'
    :param path:  SVN 仓库的相对路径
    :param standard_dirs: 用于识别分支的标准目录名称列表，默认是 ['trunk', 'branches', 'tags']
    """

    # 定义 SVN 常用的目录
    if standard_dirs is None:
        standard_dirs = ['trunk', 'branches', 'tags', ]

    # 去除开头的 '/'
    if path.startswith('/'):
        path = path[1:]

    # 分割路径
    path_parts = path.split('/')

    if not path_parts:
        return None  # 空路径

    # 如果第一个部分在标准目录中
    if path_parts[0] in standard_dirs:
        # 对于 'trunk'，分支名称为 'trunk'
        if path_parts[0] == 'trunk':
            branch_name = '/trunk'
        # 对于 'branches'、'tags'、'sandbox'，包括下一级目录作为分支名称
        elif len(path_parts) >= 2:
            branch_name = f"/{path_parts[0]}/{path_parts[1]}"
        else:
            # 如果没有下一级目录，则仅返回标准目录名
            branch_name = f'/{path_parts[0]}'
    else:
        # 如果不在标准目录中，可能是自定义目录，返回第一个部分
        branch_name = f'/{path_parts[0]}'  # 自定义目录

    return branch_name


def get_svn_branch_path(path, branch_dirs=None, depth=None):
    """
    获取指定路径下SVN仓库的分支路径。

    参数：
    - path: 工作副本的本地路径.
    例如：path = r"D:\svn_project_test\MyDataSVN\trunk\RootFolder"
    - branch_dirs: 用于识别分支的目录名称列表，默认是 ['branches', 'tags', 'trunk']
    - depth: 指定需要获取的路径深度，如果为 None，则获取到分支目录下一级

    返回值：
    - branch_path: 分支的相对路径（例如 '/trunk'、'/branches/release1.1'），如果未能识别，则返回整个相对路径
    """
    if branch_dirs is None:
        branch_dirs = ['branches', 'tags', 'trunk']

    try:
        # 执行 'svn info' 命令
        result = subprocess.run(['svn', 'info', path],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=SUBPROCESS_ENV)
        if result.returncode != 0:
            print(f"执行 svn info 时出错：{result.stderr}")
            return None

        # 解析输出，获取URL和仓库根
        url = None
        repo_root = None
        for line in result.stdout.splitlines():
            if line.startswith('URL:'):
                url = line.split('URL:')[1].strip()
            elif line.startswith('Repository Root:'):
                repo_root = line.split('Repository Root:')[1].strip()
            if url and repo_root:
                break

        if not url or not repo_root:
            print("无法在 svn info 输出中找到 URL 或 Repository Root。")
            return None

        # 获取相对于仓库根的路径
        relative_path = url[len(repo_root):].strip('/')
        path_parts = relative_path.split('/')

        # 查找第一个匹配的分支目录
        for i, part in enumerate(path_parts):
            if part in branch_dirs:
                # 根据 depth 参数确定返回的路径
                if depth is None:
                    branch_path = '/' + '/'.join(path_parts[:i + 2])  # 默认获取到分支目录下一级
                else:
                    branch_path = '/' + '/'.join(path_parts[:i + depth])
                return branch_path

        # 如果未找到匹配的分支目录，则返回整个相对路径
        return '/' + relative_path

    except Exception as e:
        print(f"发生异常：{e}")
        return None
