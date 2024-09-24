import os.path

from maya_client.maya_data import MayaData
from svn_client.svn_utils import get_local_file_svn_info, list_svn_files, update_to_revision, cleanup
from settings import MayaClientSettings


class LocalSVNUtilities:
    def __init__(self, ):
        '''
        将本地仓库更新为特定版本
        '''

    @classmethod
    def update_to_revision(cls, revision: int | str, repo_path: str):
        '''
        如果当前revision与被要求更新的版本不一样。则更新本地svn
        :return:
        '''
        cleanup(repo_path)
        result = get_local_file_svn_info(repo_path, )
        if int(result.revision) != revision:
            update_to_revision(revision, repo_path)

    def get_maya_file_list(self, repo_path, full_path=True):
        result = []
        for _ in list_svn_files(repo_path):
            if _.endswith('.ma') or _.endswith('.mb'):
                path = _
                if full_path:
                    path = os.path.join(repo_path, _)
                path = path.replace('\\', '/')
                result.append(path)
        return result


def local_process_main():
    results = []
    l = LocalSVNUtilities()
    # repo_path = 'D:\svn_project_test\MyDataSVN_trunk'
    repo_paths = MayaClientSettings.get_local_svn_repo_path()
    revision = 18
    for repo_path in repo_paths:
        for local_repo_path in repo_path.LOCAL_SVN_REPO_PATH_LIST:
            l.update_to_revision(revision, local_repo_path)
            for i in l.get_maya_file_list(local_repo_path):
                file_info = get_local_file_svn_info(i)
                d = {
                    'repository_name': repo_path.REPO_NAME,
                    'commit_revision': file_info.last_change_rev,
                    'path': file_info.relative_url,
                    'local_path': i
                }
                d.update(MayaData().get_data(i))
                results.append(d)
    return results


if __name__ == '__main__':
    local_process_main()
