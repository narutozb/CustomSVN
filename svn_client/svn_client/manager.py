# manager.py

import dataclasses
import logging
from typing import List

from apis import SvnApis
from config import SVNClientConfig

from apis.client_base import ClientBase

from svn_client.dc import CommitLogToServerDC
from svn_client.status_manager import StatusManager

from svn_client.exceptions import SVNUpdateError
from svn_client.svn_utils import get_latest_svn_revision, get_svn_log2, calculate_size, parse_svn_log2

logger = logging.getLogger(__name__)


class SVNManager(ClientBase):
    def __init__(self, svn_client_config: SVNClientConfig, status_manager: StatusManager):
        super().__init__()
        self.config = svn_client_config
        self.status_manager = status_manager
        self.apis = SvnApis(self)
        self.__latest_revision_from_server: int = self.get_existing_revision()

    def get_start_revision(self) -> int:
        start_revision = self.config.START_REVISION
        existing_latest_revision = self.__latest_revision_from_server
        if start_revision and 0 < start_revision <= existing_latest_revision and self.config.FORCE_UPDATE:
            return start_revision
        elif not start_revision and not existing_latest_revision:
            return 1
        else:
            return existing_latest_revision

    def get_end_revision(self) -> int:
        if self.config.END_REVISION and self.config.END_REVISION < self.__latest_revision_from_server:
            return self.config.END_REVISION
        else:
            latest_revision = get_latest_svn_revision(self.config.REPO_ROOT_URL)
            if latest_revision is None:
                logger.error('无法获取 SVN 最新修订版本。')
                raise SVNUpdateError('无法获取 SVN 最新修订版本。')
            return latest_revision

    def get_commits_data(self) -> List[dict]:
        start_revision = self.get_start_revision()
        end_revision = self.get_end_revision()

        if end_revision - start_revision > self.config.COMMITS_SPLIT_NUM:
            update_to_end_revision = start_revision + self.config.COMMITS_SPLIT_NUM - 1
        else:
            update_to_end_revision = end_revision

        if start_revision >= update_to_end_revision:
            self.config.increment_svn_update_interval()
            return []

        logger.info(
            f'获取 {self.config.REPO_NAME_CUSTOM_SERVER} 的 SVN 数据，修订版本从 {start_revision} 到 {update_to_end_revision}')
        self.config.set_default_svn_update_interval()

        xml_data = get_svn_log2(self.config.REPO_ROOT_URL, start_revision, update_to_end_revision)
        commits = parse_svn_log2(xml_data)

        result = [
            dataclasses.asdict(
                CommitLogToServerDC(
                    **dataclasses.asdict(commit),
                    repo_name=self.config.REPO_NAME_CUSTOM_SERVER,
                    svn_client_version=self.config.CLIENT_VERSION,
                )
            )
            for commit in commits
        ]

        return result

    def update_commits_data(self) -> None:
        self.status_manager.start_upload()
        logger.debug(f'{self.config.REPO_NAME_CUSTOM_SERVER}:开始上传提交数据。')
        try:
            commits_data = self.get_commits_data()
            __div_data_size = 0
            div_data = []

            for idx, commit in enumerate(commits_data):
                __div_data_size += calculate_size(commit)
                div_data.append(commit)

                if idx == len(commits_data) - 1 or __div_data_size > self.config.MAX_UPDATE_PER_COMMITS_DATA_SIZE:
                    logger.info(f'上传数据，修订版本从 {div_data[0]["revision"]} 到 {div_data[-1]["revision"]}')
                    self.apis.update_commits(data=div_data)
                    div_data = []
                    __div_data_size = 0

            # 上传数据成功后，更新 self.__latest_revision_from_server
            self.__latest_revision_from_server = self.get_existing_revision()
            logger.debug(f'更新后，服务器上的最新修订版本: {self.__latest_revision_from_server}')

        except Exception as e:
            logger.error(f'更新提交数据时出错: {e}')
            raise
        finally:
            self.status_manager.end_upload()
            logger.debug('提交数据上传完成。')

    def get_existing_revision(self) -> int:
        latest_commit = self.apis.get_repository_latest_commit_by_repo_name(self.config.REPO_NAME_CUSTOM_SERVER)
        if latest_commit:
            logger.debug(f'服务器上的最新修订版本: {latest_commit.revision}')
            return latest_commit.revision
        else:
            logger.debug('服务器上未找到现有修订版本。')
            return 0
