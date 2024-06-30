import sys
import time
import threading
from config import Config
from manager import SVNManager
from status_manager import StatusManager

# 标志位，用于控制程序是否正在运行
running = True


def main():
    global running
    status_manager = StatusManager()
    manager = SVNManager(status_manager)
    print('manager finished')

    def upload_data():
        print('run upload_data')
        while running:
            try:
                manager.update_svn_data()
                # Check if the current revision has reached or exceeded Config.END_REVISION
                if Config.END_REVISION is not None and manager.get_existing_revision() >= Config.END_REVISION:
                    print(f"Current revision has reached or exceeded END_REVISION ({Config.END_REVISION}). Stopping...")
                    break
                if Config.RUN_ONCE:
                    break
            except Exception as e:
                print(f"Error: {e}")
                # 如果报错的话，则退出程序
                sys.exit(1)

            time.sleep(Config.SVN_UPDATE_INTERVAL)

    # 创建并启动上传数据的线程
    upload_thread = threading.Thread(target=upload_data)
    upload_thread.start()

    try:
        while running:
            if Config.RUN_ONCE and not upload_thread.is_alive():
                running = False
            print('sleep1...')
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program...")
        running = False
        while status_manager.is_uploading():
            print("Waiting for upload to finish...")
            time.sleep(1)
        # 等待上传线程完成
        upload_thread.join()

    print("Program terminated.")


if __name__ == '__main__':
    main()
