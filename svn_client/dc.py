import dataclasses


@dataclasses.dataclass
class SVNInfoLocalDC:
    '''
    本地SVN信息
    '''
    url: str = None
    revision: int = None
    schedule: str = None
    last_changed_author: str = None
    last_change_rev: int = None
    last_changed_date: str = None
    node_kind: str = None
    relative_url: str = None


@dataclasses.dataclass
class SVNInfoLocalExtDC:
    '''
    除了必要的本地参数以外添加必要的自定义服务器所需要的属性
    '''
    path: str = None
    revision: int = None


@dataclasses.dataclass
class CommitLogDC:
    revision: int
    author: str
    date: str
    message: str
    branch_name: str | None = None
    file_changes: list['FileChangeDC'] = None


@dataclasses.dataclass
class CommitLogToServerDC(CommitLogDC):
    '''
    向自定义服务器发送的数据类,与原始数据的不同之处是添加了自定义客户端的查询字段
    '''
    repo_name: str = None
    svn_client_version: str = None


@dataclasses.dataclass
class FileChangeDC:
    path: str
    kind: str
    action: str


@dataclasses.dataclass
class FBXClientConfigDC:
    repo: 'RepositoryCustomVerifyDC'
    version: str = '0.0.3'  # 客户端版本号
    local_svn_path = r'D:\svn_project_test\MyDataSVN'  # 本地仓库路径
    FILE_SUFFIXES = ['.fbx', ]


@dataclasses.dataclass
class RepositoryCustomVerifyDC:
    name: str
    url: str


@dataclasses.dataclass
class RepoPathSettings:
    '''
    maya_settings.yaml中的REPO_PATH的设定
    '''
    REPO_NAME: str
    LOCAL_SVN_REPO_PATH_LIST: list[str]


@dataclasses.dataclass
class FileChangeFromServerDC:
    id: int
    commit: int
    path: str
    action: str
