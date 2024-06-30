# config.py
import dataclasses
import os


class Config:
    COMMITS_SPLIT_NUM = 3
    ROOT_URL = 'http://127.0.0.1:8000'  # 'http://127.0.0.1:8000'

    REPO_URL = 'https://QIAOYUANZHEN/svn/TestRepoMany/'  # 自定义服务器端的url标识
    REPO_ROOT_URL = 'https://QIAOYUANZHEN/svn/TestRepoMany/'
    LOCAL_REPO_URL = f'{REPO_ROOT_URL}'  # 实际的本地客户端需要上传的仓库
    REPO_NAME = 'TestRepoMany'

    # REPO_URL = 'https://qiaoyuanzhen/svn/MyDataSVN/'  # 自定义服务器端的url标识
    # REPO_ROOT_URL = 'https://qiaoyuanzhen/svn/MyDataSVN/'
    # LOCAL_REPO_URL = f'{REPO_ROOT_URL}'  # 实际的本地客户端需要上传的仓库
    # REPO_NAME = 'MyDataSVN'

    USERNAME = 'admin'
    PASSWORD = 'adminadmin'
    MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB in bytes
    START_REVISION = None  # 默认起始 revision
    END_REVISION = 50  # 默认终止 revision
    MAYA_DATA_API_URL = f'{ROOT_URL}/'
    SVN_UPDATE_INTERVAL = 5  # svn检查和更新数据的间隔。秒
    RUN_ONCE = False  # 新增选项，控制程序是否只运行一次

    IGNORED_PATHS = [
        '.svn',
    ]  # 忽略的路径，在此列表中的路径不会被SVNManager处理

    @classmethod
    def get_repo_root_url(cls):
        return cls.REPO_ROOT_URL.lower()


# 设置英语为环境语言
SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV["LANG"] = "en_US.UTF-8"
SUBPROCESS_ENV["LC_ALL"] = "en_US.UTF-8"


@dataclasses.dataclass
class SVNClientConfig:
    REPO_ROOT_URL: str
    REPO_NAME_CUSTOM_SERVER: str
    START_REVISION: int = None
    END_REVISION: int = None  # 当设置此时，RUN_ONCE 应自动设为 True
    COMMITS_SPLIT_NUM: int = 1
    CLIENT_VERSION: str = '0.0.1'
    RUN_ONCE: bool = False  #

    def __post_init__(self):
        if self.END_REVISION:
            self.RUN_ONCE = True
