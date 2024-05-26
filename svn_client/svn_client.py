import subprocess
import json
import sys
import requests
from datetime import datetime
from config import Config


def get_token(session, username, password):
    response = session.post(Config.API_URL + 'api-token-auth/', data={'username': username, 'password': password})
    if response.status_code == 200:
        return response.json().get('token')
    return None


def get_latest_revision(session, repo_name, headers):
    response = session.get(Config.API_URL + f'repositories/{repo_name}/latest_revision/', headers=headers)
    if response.status_code == 200:
        return response.json().get('latest_revision')
    return None


def get_svn_log(repo_url, start_revision=None):
    cmd = ['svn', 'log', repo_url, '--xml']
    if start_revision:
        cmd.extend(['-r', f'{start_revision}:HEAD'])
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout


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
    result = subprocess.run(['svn', 'diff', repo_url, '-c', revision, '--summarize'], stdout=subprocess.PIPE)
    changes = []
    for line in result.stdout.decode().splitlines():
        change_type, file_path = line.split()[:2]
        changes.append({'file_path': file_path, 'change_type': change_type})
    return changes


def get_latest_svn_revision(repo_url):
    result = subprocess.run(['svn', 'info', '--show-item', 'revision', repo_url], stdout=subprocess.PIPE)
    return int(result.stdout.strip())


def repository_exists(session, repo_name, repo_url, headers):
    url = Config.API_URL + 'repositories/'
    while url:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            repositories = data.get('results', [])
            print("Repositories from server:", repositories)  # Debug: print the repositories
            if isinstance(repositories, list):
                for repo in repositories:
                    if isinstance(repo, dict) and repo['name'] == repo_name and repo['url'] == repo_url:
                        return True
            url = data.get('next')
        else:
            return False
    return False


def calculate_size(data):
    return sys.getsizeof(json.dumps(data))


def main():
    session = requests.Session()

    token = get_token(session, Config.USERNAME, Config.PASSWORD)
    if not token:
        print("Failed to get token")
        return

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    if not repository_exists(session, Config.REPO_NAME, Config.REPO_URL, headers):
        print(f"Repository {Config.REPO_NAME} with URL {Config.REPO_URL} does not exist on the server.")
        return

    latest_revision = get_latest_revision(session, Config.REPO_NAME, headers)
    if latest_revision is not None:
        start_revision = int(latest_revision) + 1
    else:
        start_revision = None

    latest_svn_revision = get_latest_svn_revision(Config.REPO_URL)

    if start_revision and start_revision > latest_svn_revision:
        print(f"SVN repository does not have revisions greater than {latest_svn_revision}")
        return

    log_data = get_svn_log(Config.REPO_URL, start_revision=start_revision)
    commits = parse_svn_log(log_data)

    if not commits:
        print("No new commits to upload.")
        return

    for commit in commits:
        commit['file_changes'] = get_svn_changes(Config.REPO_URL, commit['revision'])

    data = {
        'repository': {
            'name': Config.REPO_NAME,
            'url': Config.REPO_URL,
            'description': 'Test repository'
        },
        'commits': []
    }

    current_size = calculate_size(data)

    for commit in commits:
        commit_size = calculate_size(commit)
        if current_size + commit_size > Config.MAX_UPLOAD_SIZE:
            response = session.post(Config.API_URL + 'receive_svn_data/', json=data, headers=headers)
            try:
                print(response.status_code, response.json())
            except requests.exceptions.JSONDecodeError:
                print(response.status_code, response.text)  # 打印非JSON响应
            data['commits'] = []
            current_size = calculate_size(data)
        data['commits'].append(commit)
        current_size += commit_size

    if data['commits']:
        response = session.post(Config.API_URL + 'receive_svn_data/', json=data, headers=headers)
        try:
            print(response.status_code, response.json())
        except requests.exceptions.JSONDecodeError:
            print(response.status_code, response.text)  # 打印非JSON响应


if __name__ == '__main__':
    main()
