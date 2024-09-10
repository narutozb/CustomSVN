import time
import requests
from config import Config
from endpoints import Endpoints


class ClientBase:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.token_expiry = 0
        self.login()

    def login(self):
        print('登陆中...')
        response = self.session.post(Endpoints.get_api_url(Endpoints.token_auth),
                                     data={'username': Config.USERNAME, 'password': Config.PASSWORD})
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access')
            # 假设 token 有效期为 1 小时，实际应从服务器响应中获取
            self.token_expiry = time.time() + 3600

            self.session.headers.update(self.headers)
        else:
            raise Exception("Failed to get token")

    def ensure_authenticated(self):
        if not self.token or time.time() > self.token_expiry:
            self.login()

    @property
    def headers(self):
        self.ensure_authenticated()
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
