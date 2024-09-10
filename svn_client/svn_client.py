import sys
import threading
import time

from config import SVNClientConfig
from manager import SVNManager
from status_manager import StatusManager


def main():
    running = True
    config1 = SVNClientConfig(
        REPO_NAME_CUSTOM_SERVER='TestRepoMany',
        REPO_ROOT_URL='https://QIAOYUANZHEN/svn/TestRepoMany/',
    )
    config2 = SVNClientConfig(
        REPO_NAME_CUSTOM_SERVER='MyDataSVN',
        REPO_ROOT_URL='https://QIAOYUANZHEN/svn/MyDataSVN/',
    )
    config3 = SVNClientConfig(
        REPO_NAME_CUSTOM_SERVER='redmine',
        REPO_ROOT_URL='https://svn.redmine.org/redmine/',
    )
    configs = [config2]  # config2]#, config3]

    def upload_data(config: SVNClientConfig):
        status_manager = StatusManager()
        manager = SVNManager(config, status_manager=status_manager)
        while running:
            try:
                # 主要处理
                manager.update_commits_data()
                if config.RUN_ONCE:
                    break  # 完成一次更新后退出循环
                print(f'{config.REPO_NAME_CUSTOM_SERVER}开始休眠:{config.SVN_UPDATE_INTERVAL}秒')
                time.sleep(config.SVN_UPDATE_INTERVAL)

            except Exception as e:
                print(f'Error:{e}')
                sys.exit(1)

    for _conf in configs:
        upload_thread = threading.Thread(target=upload_data, args=[_conf])
        upload_thread.start()

    try:
        while running:
            # if config.RUN_ONCE and not upload_thread.is_alive():
            #     print('触发停止')
            #     running = False
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting program....')
        running = False
        # while status_manager.is_uploading():
        #     print('手动终止，is_uploading{status_manager.is_uploading()}')
        #     time.sleep(1)
        print('Program terminated')


if __name__ == "__main__":
    main()
