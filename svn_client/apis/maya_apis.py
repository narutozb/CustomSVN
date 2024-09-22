from dataclasses import asdict

from apis.base import ApisBase
from apis.client_base import ClientBase


class MayaApis(ApisBase):
    def __init__(self, client: ClientBase):
        super().__init__(client)

    def get_earliest_commit_without_mayafile(self, params: dict):
        repo_id: int = params.get('repo_id')
        url = f'maya/mayafile/query/earliest_commit_without_mayafile/'
        response = self.client.make_request('GET', url=url, params=params)
        return response.json()
