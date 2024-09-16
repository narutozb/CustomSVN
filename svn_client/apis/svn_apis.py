# apis/svn_apis.py

from .base import ApisBase
from dataclasses import asdict
from typing import Optional
from dc import QueryRepositoriesFilter, CommitQueryS  # 导入数据类
from client_base import ClientBase

class SvnApis(ApisBase):
    def __init__(self, client: ClientBase):
        super().__init__(client)

    def get_repositories(self, params: Optional[QueryRepositoriesFilter] = None):
        '''
        获取仓库列表
        '''
        url = f'svn/repositories_query/'
        params_dict = asdict(params) if params else {}
        response = self.client.make_request('GET', url=url, params=params_dict)
        results = response.json()
        return results

    def get_repository_latest_commit(self, repo_id: int):
        '''
        获取特定仓库的最后一个commit
        '''
        url = f'svn/repositories_query/{repo_id}/latest_commit/'
        response = self.client.make_request('GET', url)
        results = CommitQueryS(**response.json())
        return results

    def get_repository_latest_commit_by_repo_name(self, repo_name: str):
        '''
        通过仓库名字获取仓库的最后一个commit数据
        '''
        results = self.get_repositories(QueryRepositoriesFilter(name=repo_name)).get('results')
        if len(results) == 1:
            return self.get_repository_latest_commit(results[0].get('id'))
        else:
            print('Repository仓库名称错误')

    def update_commits(self, data: list[dict]):
        '''
        上传和创建或者更新commits的api
        '''
        url = f'svn/receive_commits/'
        response = self.client.make_request('POST', url, json=data)
        return response.json()
