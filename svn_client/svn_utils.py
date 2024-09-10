import subprocess
import json
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET

from config import SUBPROCESS_ENV
from dc import SVNInfoLocalDC, CommitLogDC, FileChangeDC
from exceptions import SVNUpdateError


def get_svn_log(repo_url, start_revision=None, end_revision=None):
    if not start_revision:
        start_revision = 1

    if not end_revision:
        end_revision = 'HEAD'

    cmd = ['svn', 'log', repo_url, '--xml']

    cmd.extend(['-r', f'{start_revision}:{end_revision}'])
    print(' '.join(cmd))

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return handle_encoding(result.stdout)


def get_svn_log2(repo_url, start_revision=None, end_revision=None):
    if not start_revision:
        start_revision = 1

    if not end_revision:
        end_revision = 'HEAD'

    cmd = ['svn', 'log', repo_url, '--verbose', '--xml', ]

    cmd.extend(['-r', f'{start_revision}:{end_revision}'])

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return handle_encoding(result.stdout)


def parse_svn_log(xml_data):
    root = ET.fromstring(xml_data)
    commits = []
    for entry in root.findall('logentry'):
        revision = entry.get('revision')
        author = entry.find('author').text
        date = entry.find('date').text
        msg = entry.find('msg').text
        commit = {
            'revision': revision,
            'author': author,
            'date': date,
            'message': msg,
            'file_changes': []
        }
        commits.append(commit)
    return commits


def get_commit_branch_name(file_path: str, revision: int):
    '''
    从changed path 获取其分支名称
    :param commit:
    :return:
    '''
    if int(revision) == 1:
        return 'root'

    split_path = file_path.split('/')
    if file_path.startswith('/trunk'):
        return '/trunk'
    else:
        return '/'.join(split_path[:3])


def parse_svn_log2(xml_data):
    root = ET.fromstring(xml_data)
    commits: list[CommitLogDC] = []
    for entry in root.findall('logentry'):
        revision = entry.get('revision')
        author = entry.find('author').text
        date = entry.find('date').text
        msg = entry.find('msg').text
        paths = entry.find('paths')
        file_changes = []
        for i in paths:
            file_changes.append(FileChangeDC(
                path=i.text,
                action=i.get('action'),
                kind=i.get('kind')
            ))

        commits.append(CommitLogDC(
            revision=revision,
            author=author,
            date=date,
            message=msg,
            branch_name=get_commit_branch_name(file_changes[0].path, revision=revision),
            file_changes=file_changes
        ))
    return commits


def __get_svn_changes(repo_url, revisions):
    all_changes = {}
    for revision in revisions:
        result = subprocess.run(['svn', 'diff', repo_url, '-c', str(revision), '--summarize'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        changes = []
        for line in handle_encoding(result.stdout).splitlines():
            change_type, file_path = line.split()[:2]
            changes.append({'file_path': unquote(file_path), 'change_type': change_type})
        all_changes[revision] = changes
    return all_changes


def get_latest_svn_revision(repo_url):
    '''
    获取svn服务器最后的revision
    :param repo_url:
    :return:
    '''
    commands = ['svn', 'info', '--show-item', 'revision', repo_url]
    result = subprocess.run(commands, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=SUBPROCESS_ENV)

    # print(f'{" ".join(commands)}')
    if result.stdout.strip():
        return int(result.stdout.strip())
    else:
        print("Error: SVN command did not return a result.")
        return None


def calculate_size(data):
    return sys.getsizeof(json.dumps(data))


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
        # print(f'更新成功!仓库{repo_path}到revision:{revision}')
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
