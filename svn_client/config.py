# config.py

class Config:
    ROOT_URL = 'http://127.0.0.1:8000'
    API_URL = f'{ROOT_URL}/api/'

    REPO_URL = 'https://qiaoyuanzhen/svn/TestRepo/' #
    REPO_NAME = 'TestRepo'
    # REPO_URL = 'https://QIAOYUANZHEN/svn/TESTREPO1/'
    # REPO_NAME = 'TESTREPO1'
    USERNAME = 'admin'
    PASSWORD = 'adminadmin'
    MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB in bytes
