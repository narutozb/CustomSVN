import os.path
from urllib.parse import unquote

import requests
from config import Config
from endpoints import Endpoints
from svn_utils import (
    get_token, get_latest_revision, get_svn_log, parse_svn_log,
    get_svn_changes, calculate_size, get_latest_svn_revision
)
from status_manager import StatusManager


class SVNManager:
    def __init__(self, status_manager):
        self.session = requests.Session()
        self.token = get_token(self.session, Config.USERNAME, Config.PASSWORD)
        if not self.token:
            raise Exception("Failed to get token")
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        self.status_manager = status_manager

    def get_existing_revision(self):
        latest_revision = get_latest_revision(self.session, Config.REPO_NAME, self.headers)
        return int(latest_revision) if latest_revision is not None else None

    def decode_url(self, url):
        return unquote(url)

    def update_svn_data(self):
        self.status_manager.start_upload()

        try:
            if Config.START_REVISION is not None:
                start_revision = Config.START_REVISION
            else:
                start_revision = self.get_existing_revision()
                if start_revision is not None:
                    start_revision += 1
                else:
                    start_revision = 1

            end_revision = Config.END_REVISION or get_latest_svn_revision(Config.LOCAL_REPO_URL)
            if start_revision > end_revision:
                print(f"No new revisions to update. Current latest revision is {end_revision}.")
                return

            log_data = get_svn_log(Config.LOCAL_REPO_URL, start_revision=start_revision)
            commits = parse_svn_log(log_data)
            if not commits:
                print("No new commits to upload.")
                return

            # Get file changes for all commits at once
            all_file_changes = get_svn_changes(Config.LOCAL_REPO_URL, [commit['revision'] for commit in commits])

            for commit in commits:
                # Use the pre-fetched file changes
                commit['file_changes'] = all_file_changes[commit['revision']]

                # Add branch name to commit
                if commit['file_changes']:
                    file_path: str = commit['file_changes'][0]['file_path']
                    branch_name = None
                    file_path_replaced = file_path.replace(Config.LOCAL_REPO_URL, '')
                    if file_path_replaced.startswith('trunk'):
                        branch_name = 'trunk'

                    elif file_path_replaced.startswith('branches'):
                        split_file_path_replaced = file_path_replaced.split('/')
                        if len(split_file_path_replaced) > 2:
                            branch_name = split_file_path_replaced[1]

                    commit['branch_name'] = branch_name

            data = {
                'repository': {
                    'name': Config.REPO_NAME,
                    'url': Config.REPO_URL,
                },

                'commits': []
            }

            current_size = calculate_size(data)
            for commit in commits:
                commit_size = calculate_size(commit)
                if current_size + commit_size > Config.MAX_UPLOAD_SIZE:
                    response = self.session.post(Endpoints.get_api_url(Endpoints.svn_receive_svn_data), json=data,
                                                 headers=self.headers)
                    try:
                        print(response.status_code, response.json())
                    except requests.exceptions.JSONDecodeError:
                        print(response.status_code, response.text)  # 打印非JSON响应
                    data['commits'] = []
                    current_size = calculate_size(data)
                print(commit)
                data['commits'].append(commit)
                current_size += commit_size

            if data['commits']:
                response = self.session.post(Endpoints.get_api_url(Endpoints.svn_receive_svn_data), json=data,
                                             headers=self.headers)
                try:
                    print(response.status_code, response.json())
                except requests.exceptions.JSONDecodeError:
                    print(response.status_code, response.text)  # 打印非JSON响应
        finally:
            self.status_manager.end_upload()
