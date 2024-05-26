import os
import random
import subprocess

# 全局参数
REPO_URL = r'https://QIAOYUANZHEN/svn/TESTREPO1/'
CHECKOUT_PATH = r'D:\test_repo\testrepo1'
GENERATE_MAX_FILE = 200
GENERATE_MAX_COMMITS = 500
MAX_MODIFICATIONS = 50
MAX_FILES_PER_COMMIT = 200  # 每次提交的最大文件数量


def checkout_svn_repository(repo_url, checkout_path):
    subprocess.run(['svn', 'checkout', repo_url, checkout_path], check=True)


def modify_file(file_path, modification_count):
    with open(file_path, 'a') as file:
        file.write(f'\nModification {modification_count} in {os.path.basename(file_path)}')


def commit_changes(checkout_path, message):
    subprocess.run(['svn', 'commit', '-m', message, checkout_path], check=True)


def add_file(file_path):
    with open(file_path, 'w') as file:
        file.write(f'This is {os.path.basename(file_path)}')
    subprocess.run(['svn', 'add', file_path], check=True)


def delete_file(file_path):
    subprocess.run(['svn', 'delete', '--force', file_path], check=True)


def create_and_commit_files(checkout_path, max_files, max_commits, max_modifications, max_files_per_commit):
    files = [os.path.join(checkout_path, f'test_file_{i}.txt') for i in range(1, max_files + 1)]
    for commit_number in range(max_commits):
        files_in_commit = random.randint(1, max_files_per_commit)
        commit_files = random.sample(files, files_in_commit)
        commit_message = []

        for file_path in commit_files:
            file_action = random.choice(['add', 'modify', 'delete'])

            if file_action == 'add' and not os.path.exists(file_path):
                add_file(file_path)
                commit_message.append(f'Added {os.path.basename(file_path)}')

            elif file_action == 'modify' and os.path.exists(file_path):
                modification_count = random.randint(1, max_modifications)
                modify_file(file_path, modification_count)
                commit_message.append(f'Modified {os.path.basename(file_path)} {modification_count} times')

            elif file_action == 'delete' and os.path.exists(file_path):
                delete_file(file_path)
                commit_message.append(f'Deleted {os.path.basename(file_path)}')

        if commit_message:
            commit_changes(checkout_path, '; '.join(commit_message))


def generate_test_svn_data(repo_url, checkout_path, max_files, max_commits, max_modifications, max_files_per_commit):
    checkout_svn_repository(repo_url, checkout_path)
    create_and_commit_files(checkout_path, max_files, max_commits, max_modifications, max_files_per_commit)


if __name__ == '__main__':
    repo_url = REPO_URL
    checkout_path = CHECKOUT_PATH
    max_files = GENERATE_MAX_FILE
    max_commits = GENERATE_MAX_COMMITS
    max_modifications = MAX_MODIFICATIONS
    max_files_per_commit = MAX_FILES_PER_COMMIT

    generate_test_svn_data(repo_url, checkout_path, max_files, max_commits, max_modifications, max_files_per_commit)
    print(f"Generated test data in the SVN repository.")
