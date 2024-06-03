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

    def update_svn_data(self):
        self.status_manager.start_upload()

        try:
            if Config.FORCE_UPDATE:
                start_revision = 1
            elif Config.START_REVISION is not None:
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

            for commit in commits:
                commit['file_changes'] = get_svn_changes(Config.LOCAL_REPO_URL, commit['revision'])

            data = {
                'repository': {
                    'name': Config.REPO_NAME,
                    'url': Config.REPO_URL,
                    # 'description': 'Test repository'
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
