import dataclasses
import json


@dataclasses.dataclass
class FileChangeSummaryDC:
    '''
    FileChange的数据类概要

    '''
    file_path: str
    revision: int
    repo_name: str

    def __post_init__(self):
        if not isinstance(self.file_path, str):
            raise TypeError(f'Expected str, got {type(self.file_path).__name__}')
        if not isinstance(self.revision, int):
            raise TypeError(f'Expected int, got {type(self.revision).__name__}')
        if not isinstance(self.repo_name, str):
            raise TypeError(f'Expected str, got {type(self.repo_name).__name__}')
