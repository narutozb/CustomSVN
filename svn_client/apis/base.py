# apis/base.py

from client_base import ClientBase


class ApisBase:
    def __init__(self, client: ClientBase):
        self.client = client
        self.session = client.session
        self.api_url = client.base_url  # 使用 ClientBase 中的 base_url
