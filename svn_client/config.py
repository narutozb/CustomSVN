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
    COMMITS_SPLIT_NUM: int = 500  # 限制单次上传最大commit区间
    CLIENT_VERSION: str = '0.0.1'
    RUN_ONCE: bool = False  #
    FORCE_UPDATE: bool = False  # 强制更新指定区间是改为True
    MAX_UPDATE_PER_COMMITS_DATA_SIZE = 1024 * 1024 * 512
    DEFAULT_SVN_UPDATE_INTERVAL: int = 1  # 默认等待5秒后开始下一次上传任务
    DEFAULT_SVN_UPDATE_MAX_INTERVAL: int = 60  # 最大等待时间
    DEFAULT_SVN_UPDATE_INTERVAL_INCREMENT: int = 5  # 等待递增时间
    __svn_update_interval: int = DEFAULT_SVN_UPDATE_INTERVAL

    def __post_init__(self):
        if self.END_REVISION or self.FORCE_UPDATE:
            self.RUN_ONCE = True

    @property
    def SVN_UPDATE_INTERVAL(self):
        return self.__svn_update_interval

    def set_default_svn_update_interval(self):
        self.__svn_update_interval = self.DEFAULT_SVN_UPDATE_INTERVAL

    def increment_svn_update_interval(self):
        self.__svn_update_interval += self.DEFAULT_SVN_UPDATE_INTERVAL_INCREMENT
        if self.__svn_update_interval > self.DEFAULT_SVN_UPDATE_MAX_INTERVAL:
            self.__svn_update_interval = self.DEFAULT_SVN_UPDATE_MAX_INTERVAL
