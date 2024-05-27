import subprocess
import json
import sys
import requests
from datetime import datetime

def get_token(session, username, password, api_url):
    response = session.post(api_url + 'api-token-auth/', data={'username': username, 'password': password})
    if response.status_code == 200:
        return response.json().get('token')
    return None

def get_latest_revision(session, repo_name, headers, api_url):
    response = session.get(api_url + f'repositories/{repo_name}/latest_revision/', headers=headers)
    if response.status_code == 200:
        return response.json().get('latest_revision')
    return None

def get_svn_log(repo_url, start_revision=None):
    cmd = ['svn', 'log', repo_url, '--xml']
    if start_revision:
        cmd.extend(['-r', f'{start_revision}:HEAD'])
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

def get_svn_changes(repo_url, revision):
    result = subprocess.run(['svn', 'diff', repo_url, '-c', revision, '--summarize'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    changes = []
    for line in handle_encoding(result.stdout).splitlines():
        change_type, file_path = line.split()[:2]
        changes.append({'file_path': file_path, 'change_type': change_type})
    return changes

def get_latest_svn_revision(repo_url):
    result = subprocess.run(['svn', 'info', '--show-item', 'revision', repo_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return int(handle_encoding(result.stdout).strip())

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
