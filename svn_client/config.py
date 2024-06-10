# config.py

class Config:
    COMMITS_SPLIT_NUM = 50
    ROOT_URL = 'http://127.0.0.1:8000'  # 'http://127.0.0.1:8000'

    REPO_URL = 'https://qiaoyuanzhen/svn/MyDataSVN/'  # 自定义服务器端的url标识
    REPO_ROOT_URL = 'https://qiaoyuanzhen/svn/MyDataSVN/'
    LOCAL_REPO_URL = f'{REPO_ROOT_URL}'  # 实际的本地客户端需要上传的仓库
    REPO_NAME = 'MyDataSVN'
    USERNAME = 'admin'
    PASSWORD = 'adminadmin'
    MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB in bytes
    START_REVISION = 1  # 默认起始 revision
    END_REVISION = 20  # 默认终止 revision
    MAYA_DATA_API_URL = f'{ROOT_URL}/'
    SVN_UPDATE_INTERVAL = 15  # svn检查和更新数据的间隔。秒
    RUN_ONCE = True  # 新增选项，控制程序是否只运行一次

    IGNORED_PATHS = [
        '.svn',
    ]  # 忽略的路径，在此列表中的路径不会被SVNManager处理

    @classmethod
    def get_repo_root_url(cls):
        return cls.REPO_ROOT_URL.lower()
