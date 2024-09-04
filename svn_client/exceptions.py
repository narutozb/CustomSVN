class SVNUpdateError(Exception):
    """当 SVN 更新失败时抛出此异常"""
    def __init__(self, message):
        super().__init__(message)
