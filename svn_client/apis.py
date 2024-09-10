import dataclasses
import time
from collections import namedtuple

from requests.sessions import Session
from config import Config
from dc import QueryRepositoriesFilter, CommitQueryS


class ApisBase:
    root_url = Config.ROOT_URL
    api_url = f'{root_url}/api/'

    def __init__(self, session: Session):
        self.session = session


class SvnApis(ApisBase):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_repositories(self, params: QueryRepositoriesFilter = None):
        '''
        获取仓库列表
        :return:
        '''
        url = f'{self.api_url}svn/repositories_query/'
        results = self.session.get(url=url, params=dataclasses.asdict(params)).json()
        return results

    def get_repository_latest_commit(self, repo_id: int | str):
        '''
        获取特定仓库的最后一个commit
        :param repo_id:
        :return:
        '''
        url = f'{self.api_url}svn/repositories_query/{repo_id}/latest_commit/'
        results = CommitQueryS(**self.session.get(url).json())
        return results

    def get_repository_latest_commit_by_repo_name(self, repo_name: str):
        '''
        通过仓库名字获取仓库的最后一个commit数据
        :param repo_name:
        :return:
        '''
        results = self.get_repositories(QueryRepositoriesFilter(name=repo_name)).get('results')
        if len(results) == 1:
            return self.get_repository_latest_commit(results[0].get('id'))
        else:
            print('Repository仓库名称错误')

    def update_commits(self, data: list[dict] = None):
        '''
        上传和创建或者更新commits的api
        :param data:
        :return:
        '''
        self.session.post(f'{self.api_url}svn/receive_commits/', json=data)


class UserApis(ApisBase):
    def __init__(self, session: Session):
        super().__init__(session)
        pass
