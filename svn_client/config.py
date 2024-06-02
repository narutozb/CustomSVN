# config.py

class Config:
    ROOT_URL = 'http://127.0.0.1:8000'
    API_URL = f'{ROOT_URL}/api/'

    REPO_URL = 'https://QIAOYUANZHEN/svn/MyDataSVN/'  # 自定义服务器端的url标识
    LOCAL_REPO_URL = 'https://QIAOYUANZHEN/svn/MyDataSVN/trunk/'  # 实际的本地客户端需要上传的仓库
    REPO_NAME = 'MyDataSVN'
    USERNAME = 'admin'
    PASSWORD = 'adminadmin'
    MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB in bytes
    FORCE_UPDATE = False  # 默认不强制更新
    START_REVISION = None  # 默认起始 revision
    END_REVISION = None  # 默认终止 revision
    MAYA_DATA_API_URL = f'{ROOT_URL}/'
    SVN_UPDATE_INTERVAL = 15  # svn检查和更新数据的间隔。秒
    RUN_ONCE = False  # 新增选项，控制程序是否只运行一次

    IGNORED_PATHS = [
        '.svn',
    ]  # 忽略的路径，在此列表中的路径不会被SVNManager处理
