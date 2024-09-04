import dataclasses
import os.path

import yaml

from dc import RepoPathSettings


class MayaClientSettings:
    yaml_path = 'maya_settings.yaml'
    # 打开YAML文件
    with open(yaml_path, 'r') as file:
        # 使用yaml.safe_load()函数加载YAML内容
        data = yaml.safe_load(file)

    @classmethod
    def get_maya_interpreter_path(cls) -> str:
        # Maya的解释器地址
        return cls.data.get('INTERPRETER').get('MAYA')

    @classmethod
    def get_local_svn_repo_path(cls):
        result = []
        for i in cls.data.get('REPO_PATH'):
            result.append(RepoPathSettings(i.get('REPO_NAME'), i.get('LOCAL_SVN_REPO_PATH')))
        return result
