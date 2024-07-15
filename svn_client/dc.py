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
    last_change_rev: str = None
    last_changed_date: str = None
    node_kind: str = None
    relative_url: str = None


@dataclasses.dataclass
class SVNInfoLocalExtDC:
    '''
    除了必要的本地参数以外添加必要的自定义服务器所需要的属性
    '''
    file_path: str = None
    revision: int = None
    repo_name: str = None


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
