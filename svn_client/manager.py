import requests
from config import Config
from endpoints import Endpoints
from login import ClientBase
from svn_utils import (
    get_token, get_latest_revision, get_svn_log, parse_svn_log,
    get_svn_changes, calculate_size, get_latest_svn_revision
)


class SVNManager(ClientBase):
    def __init__(self):
        super().__init__()

    def get_existing_revision(self):
        latest_revision = get_latest_revision(self.session, Config.REPO_NAME, self.headers, Config.API_URL)
        return int(latest_revision) if latest_revision is not None else None

    def update_svn_data(self):
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

        end_revision = Config.END_REVISION or get_latest_svn_revision(Config.REPO_URL)

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
        print('Current size:', current_size, 'Max size:', Config.MAX_UPLOAD_SIZE)
        for commit in commits:
            commit_size = calculate_size(commit)
            if current_size + commit_size > Config.MAX_UPLOAD_SIZE:
                response = self.session.post(
                    Endpoints.get_api_url(Endpoints.svn_receive_svn_data), json=data, headers=self.headers)
                try:
                    print(response.status_code, response.json())
                except requests.exceptions.JSONDecodeError:
                    print(response.status_code, response.text)  # 打印非JSON响应
                data['commits'] = []
                current_size = calculate_size(data)
            data['commits'].append(commit)
            current_size += commit_size

        if data['commits']:
            response = self.session.post(
                Endpoints.get_api_url(Endpoints.svn_receive_svn_data),
                json=data,
                headers=self.headers)
            try:
                print(response.status_code, response.json())
            except requests.exceptions.JSONDecodeError:
                print(response.status_code, response.text)  # 打印非JSON响应
