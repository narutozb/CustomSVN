# main_svn_client.py

import sys
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from config import SVNClientConfig
from svn_client.exceptions import SVNUpdateError
from svn_client.manager import SVNManager
from svn_client.status_manager import StatusManager

logger = logging.getLogger(__name__)

stop_event = threading.Event()

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

    configs = [
        SVNClientConfig(
            REPO_NAME_CUSTOM_SERVER='MyDataSVN',
            REPO_ROOT_URL='https://QIAOYUANZHEN/svn/MyDataSVN/',
        ),
        SVNClientConfig(
            REPO_NAME_CUSTOM_SERVER='TestRepoMany',
            REPO_ROOT_URL='https://QIAOYUANZHEN/svn/TestRepoMany/',
        ),
        SVNClientConfig(
            REPO_NAME_CUSTOM_SERVER='redmine',
            REPO_ROOT_URL='https://svn.redmine.org/redmine/',
        ),
    ]

    def upload_data(config: SVNClientConfig):
        status_manager = StatusManager()
        manager = SVNManager(config, status_manager=status_manager)
        while not stop_event.is_set():
            try:
                manager.update_commits_data()
                if config.RUN_ONCE:
                    break
                logger.info(f'{config.REPO_NAME_CUSTOM_SERVER} 休眠 {config.SVN_UPDATE_INTERVAL} 秒。')
                stop_event.wait(timeout=config.SVN_UPDATE_INTERVAL)
            except SVNUpdateError as e:
                logger.error(f'SVNUpdateError: {e}')
                sys.exit(1)
            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                sys.exit(1)
        logger.info(f'线程 {config.REPO_NAME_CUSTOM_SERVER} 已停止。')

    with ThreadPoolExecutor(max_workers=len(configs)) as executor:
        futures = [executor.submit(upload_data, conf) for conf in configs]

        try:
            while True:
                time.sleep(0.5)
                if all(f.done() for f in futures):
                    break
        except KeyboardInterrupt:
            logger.info('由于 KeyboardInterrupt，退出程序...')
            stop_event.set()
        finally:
            logger.info('程序已终止。')

if __name__ == "__main__":
    main()
