import requests

from config import Config
from endpoints import Endpoints
from svn_utils import get_token


class ClientBase:
    def __init__(self):
        '''
        初始化 session 和 headers
        '''
        self.session = requests.Session()
        self.token = get_token(self.session, Config.USERNAME, Config.PASSWORD)
        if not self.token:
            raise Exception("Failed to get token")
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }


class TestClient(ClientBase):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    client = TestClient()
    commits = client.session.get(Endpoints.get_api_url(Endpoints.svn_commits), headers=client.headers)
    print(commits.text)
