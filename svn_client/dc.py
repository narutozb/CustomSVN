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


@dataclasses.dataclass
class SVNInfoLocalExtDC:
    '''
    除了必要的本地参数以外添加必要的自定义服务器所需要的属性
    '''
    file_path: str = None
    revision: int = None
    repo_name: str = None
