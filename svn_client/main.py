# main.py

from client_base import ClientBase
from apis import SvnApis
from dataclasses import asdict

if __name__ == '__main__':
    client = ClientBase()
    svn_apis = client.get_api(SvnApis)
    # 获取仓库列表
    repos = svn_apis.get_repositories()

    if repos.get('results'):
        for repo in repos.get('results'):
            repo_id = repo.get('id')
            repo_name = repo.get('name')
            latest_commit_by_id = svn_apis.get_repository_latest_commit(repo_id)
            print(asdict(latest_commit_by_id))
            latest_commit_by_name = svn_apis.get_repository_latest_commit_by_repo_name(repo_name)
            print(asdict(latest_commit_by_name))
