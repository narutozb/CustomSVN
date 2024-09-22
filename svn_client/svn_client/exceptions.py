# exceptions.py
class SVNError(Exception):
    """SVN 相关异常的基类。"""
    pass


class SVNUpdateError(SVNError):
    """当 SVN 更新失败时引发的异常。"""
    pass


class SVNRepositoryError(SVNError):
    """SVN 仓库错误时引发的异常。"""
    pass
