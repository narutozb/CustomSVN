import subprocess
import json
import sys
from urllib.parse import unquote

from config import SUBPROCESS_ENV
from endpoints import Endpoints
from fbx_client.fbx_tools._dc import SVNInfoLocalDC


def get_token(session, username, password):
    response = session.post(Endpoints.get_api_url(Endpoints.token_auth),
                            data={'username': username, 'password': password})
    if response.status_code == 200:
        return response.json().get('token')
    return None


def get_latest_revision(session, repo_name, headers):
    response = session.get(Endpoints.get_latest_revision_api_url(repo_name), headers=headers)
    if response.status_code == 200:
        return response.json().get('latest_revision')
    return None


def get_svn_log(repo_url, start_revision=None, end_revision=None):
    if not start_revision:
        start_revision = 1

    if not end_revision:
        end_revision = 'HEAD'

    cmd = ['svn', 'log', repo_url, '--xml']

    cmd.extend(['-r', f'{start_revision}:{end_revision}'])

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return handle_encoding(result.stdout)


def parse_svn_log(xml_data):
    import xml.etree.ElementTree as ET
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


def get_svn_changes(repo_url, revisions):
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
    commands = ['svn', 'info', '--show-item', 'revision', repo_url]
    result = subprocess.run(commands, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=SUBPROCESS_ENV)
    print(f'{" ".join(commands)}')
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


def get_local_file_svn_info(local_path: str):
    commands = ['svn', 'info', local_path]
    result = subprocess.run(commands, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, check=True, env=SUBPROCESS_ENV)

    svn_info = SVNInfoLocalDC()

    for line in result.stdout.splitlines():
        if line.startswith('URL:'):
            svn_info.url = line.split()[1]
        if line.startswith('Revision:'):
            svn_info.revision = line.split()[1]
        if line.startswith('Node Kind:'):
            svn_info.node_kind = line.split()[-1]
        if line.startswith('Schedule:'):
            svn_info.schedule = line.split()[-1]
        if line.startswith('Last Changed Author:'):
            svn_info.last_changed_author = line.split()[-1]
        if line.startswith('Last Changed Rev:'):
            svn_info.last_change_rev = line.split()[-1]
        if line.startswith('Last Changed Date:'):
            svn_info.last_changed_date = line.split(':', 1)[1].strip()

    return svn_info


def is_svn_repository(path):
    '''
    检查指定路径是否是svn仓库
    :param path:
    :return:
    '''
    result = subprocess.run(['svn', 'info', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=SUBPROCESS_ENV)
    return result.returncode == 0
