# config.py

class Config:
    ROOT_URL = 'http://127.0.0.1:8000'
    API_URL = f'{ROOT_URL}/api/'
    REPO_URL = 'https://qiaoyuanzhen/svn/TestRepo/'
    REPO_NAME = 'TestRepo'
    USERNAME = 'admin'
    PASSWORD = 'adminadmin'
    MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB in bytes
    FORCE_UPDATE = False  # 默认不强制更新
    START_REVISION = None  # 默认起始 revision
    END_REVISION = None  # 默认终止 revision
    MAYA_DATA_API_URL = f'{ROOT_URL}/'
