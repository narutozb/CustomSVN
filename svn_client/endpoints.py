class Endpoints:
    '''
    APP_ENDPOINT = ''
    '''
    root_url = 'http://127.0.0.1:8000'
    api_url = f'{root_url}/api/'
    svn_commits = 'svn/commits/'
    svn_receive_svn_data = 'svn/receive_svn_data/'

    token_auth = 'api-token-auth/'

    maya_sceneinfos = 'maya/sceneinfos/'

    @classmethod
    def get_api_url(cls, endpoint):
        '''
        获取完整的URL
        :param endpoint:
        :return:
        '''
        return cls.api_url + endpoint

    @classmethod
    def get_latest_revision_api_url(cls, repo_name):
        '''
        获取最新的版本号
        :param repo_name: 仓库名称
        :return:
        '''
        return f'{cls.api_url}svn/repositories/{repo_name}/latest_revision/'

    @classmethod
    def get_file_changes_by_repo_and_revision_api_url(cls, repo_name: str, revision: int):
        return f'{cls.api_url}svn/repositories/{repo_name}/commits/{revision}/file_changes/'

    @classmethod
    def get_maya_file_changes_by_repo_and_revision_api_url(
            cls,
            repo_name: str,
            revision: int,
            maya_client_version: str
    ):
        return f'{cls.api_url}maya/{repo_name}/{revision}/file_changes/?maya_client_version={maya_client_version}'
