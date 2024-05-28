import sys
import time
import threading
from config import Config
from manager import SVNManager

# 标志位，用于控制程序是否正在运行
running = True
uploading = False


def main():
    global running, uploading
    manager = SVNManager()

    def upload_data():
        global uploading
        while running:
            try:
                uploading = True
                manager.update_svn_data()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                uploading = False
            time.sleep(Config.SVN_UPDATE_INTERVAL)

    # 创建并启动上传数据的线程
    upload_thread = threading.Thread(target=upload_data)
    upload_thread.start()

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program...")
        running = False
        # 等待上传线程完成
        upload_thread.join()

    print("Program terminated.")


if __name__ == '__main__':
    main()
