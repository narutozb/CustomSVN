# config.py
import dataclasses
import os

# 设置英语为环境语言
SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV["LANG"] = "en_US.UTF-8"
SUBPROCESS_ENV["LC_ALL"] = "en_US.UTF-8"

from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载环境变量


class Config:
    ROOT_URL = os.getenv('ROOT_URL', 'http://127.0.0.1:8000')
    API_URL = f'{ROOT_URL}/api/'

    REPO_NAME = os.getenv('REPO_NAME', 'TestRepoMany')
    # USERNAME = os.getenv('USERNAME', 'admin')
    USERNAME = 'admin'
    PASSWORD = os.getenv('PASSWORD', 'adminadmin')
    IGNORED_PATHS = ['.svn']  # 忽略的路径

    REFRESH_THRESHOLD = int(os.getenv('REFRESH_THRESHOLD', str(3600 * 2)))  # 在令牌过期前 2 小时刷新


@dataclasses.dataclass
class SVNClientConfig:
    REPO_ROOT_URL: str
    REPO_NAME_CUSTOM_SERVER: str
    START_REVISION: int = None
    END_REVISION: int = None
    COMMITS_SPLIT_NUM: int = 500
    CLIENT_VERSION: str = '0.0.1'
    RUN_ONCE: bool = False
    FORCE_UPDATE: bool = False
    MAX_UPDATE_PER_COMMITS_DATA_SIZE: int = 1024 * 1024 * 1024
    DEFAULT_SVN_UPDATE_INTERVAL: int = 1
    DEFAULT_SVN_UPDATE_MAX_INTERVAL: int = 60
    DEFAULT_SVN_UPDATE_INTERVAL_INCREMENT: int = 5
    __svn_update_interval: int = dataclasses.field(init=False, default=1)

    def __post_init__(self):
        if self.END_REVISION or self.FORCE_UPDATE:
            self.RUN_ONCE = True

    @property
    def SVN_UPDATE_INTERVAL(self) -> int:
        return self.__svn_update_interval

    def set_default_svn_update_interval(self) -> None:
        self.__svn_update_interval = self.DEFAULT_SVN_UPDATE_INTERVAL

    def increment_svn_update_interval(self) -> None:
        self.__svn_update_interval += self.DEFAULT_SVN_UPDATE_INTERVAL_INCREMENT
        if self.__svn_update_interval > self.DEFAULT_SVN_UPDATE_MAX_INTERVAL:
            self.__svn_update_interval = self.DEFAULT_SVN_UPDATE_MAX_INTERVAL
