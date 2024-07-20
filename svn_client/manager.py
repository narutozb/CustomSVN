import dataclasses
import sys
import threading
import time

import requests
from config import SVNClientConfig, Config
from dc import CommitLogToServerDC
from endpoints import Endpoints
from login import ClientBase
from status_manager import StatusManager
from svn_utils import get_latest_svn_revision, parse_svn_log2, get_svn_log2, calculate_size, get_latest_revision


class SVNManager(ClientBase):

    def __init__(self, svn_client_config: SVNClientConfig, status_manager: StatusManager):
        super().__init__()
        self.config = svn_client_config
        self.status_manager = status_manager

    def get_start_revision(self) -> int:
        '''
        获取起始revision
        由配置选项传入起始revision，如果起始值为None那么更新则从revision1开始
        :return:
        '''
        start_revision = self.config.START_REVISION
        existing_latest_revision = self.get_existing_revision()

        if start_revision and 0 < start_revision <= existing_latest_revision and self.config.FORCE_UPDATE:
            return self.config.START_REVISION
        else:
            return existing_latest_revision

    def get_end_revision(self) -> int:
        '''
        获取结束revision
        由配置选项传入结束revision,如果指定了特定的结束revision，则检查是否存在此revision。如果存在则返回，如果不存在则返回当前svn服务器端最大revision
        :return:
        '''
        svn_latest_revision = self.get_existing_revision()

        if self.config.END_REVISION and self.config.END_REVISION < svn_latest_revision:
            return self.config.END_REVISION
        else:
            return get_latest_svn_revision(self.config.REPO_ROOT_URL)

    def get_commits_data(self):

        if self.get_end_revision() - self.get_start_revision() > self.config.COMMITS_SPLIT_NUM:
            update_to_end_revision = self.get_start_revision() + self.config.COMMITS_SPLIT_NUM - 1
        else:
            update_to_end_revision = self.get_end_revision()
        print(self.get_start_revision(), update_to_end_revision)
        # 当自定义服务器上的revision版本号大于等于SVN服务器上的revision时，无需上传数据到自定义服务器。也就是此时自定义服务器版本为最新
        if self.get_start_revision() >= update_to_end_revision:
            self.config.increment_svn_update_interval()
            return []

        print(f'获取SVN数据-{self.get_start_revision()}~{update_to_end_revision}')
        self.config.set_default_svn_update_interval()
        data = get_svn_log2(self.config.REPO_ROOT_URL, self.get_start_revision(), update_to_end_revision)
        result = []
        for d in parse_svn_log2(data):
            result.append(
                CommitLogToServerDC(**dataclasses.asdict(d),
                                    repo_name=self.config.REPO_NAME_CUSTOM_SERVER,
                                    svn_client_version=self.config.CLIENT_VERSION,
                                    )
            )
        return [dataclasses.asdict(_) for _ in result]

    def update_commits_data(self):
        '''
        上传commit函数.也是外部所调用的函数
        :return:
        '''
        self.status_manager.start_upload()
        try:
            commits_data = self.get_commits_data()
            __div_data_size = 0
            div_data = []
            for idx, i in enumerate(commits_data):
                __div_data_size += calculate_size(i)
                div_data.append(i)
                if idx == len(commits_data) - 1 or __div_data_size > self.config.MAX_UPDATE_PER_COMMITS_DATA_SIZE:
                    print(f'上传数据-{div_data[0].get("revision")}~{div_data[-1].get("revision")}')
                    # 上传数据
                    response = self.session.post(Endpoints.get_api_url(Endpoints.receive_commits), json=div_data,
                                                 headers=self.headers)
                    # 重置分割数据
                    div_data = []
                    __div_data_size = 0

        finally:
            self.status_manager.end_upload()

    def get_existing_revision(self):
        latest_revision = get_latest_revision(self.session, self.config.REPO_NAME_CUSTOM_SERVER, self.headers)
        return int(latest_revision) if latest_revision is not None else None
