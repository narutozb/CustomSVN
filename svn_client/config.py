# config.py
import dataclasses
import os


class Config:
    ROOT_URL = 'http://127.0.0.1:8000'  # 'http://127.0.0.1:8000'
    REPO_ROOT_URL = 'https://QIAOYUANZHEN/svn/TestRepoMany/'
    REPO_NAME = 'TestRepoMany'

    USERNAME = 'admin'
    PASSWORD = 'adminadmin'
    IGNORED_PATHS = [
        '.svn',
    ]  # 忽略的路径，在此列表中的路径不会被SVNManager处理



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
