import sys
from manager import SVNManager


def main():
    manager = SVNManager()
    try:
        manager.update_svn_data()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
