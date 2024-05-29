import subprocess


def run_svn_command(command, cwd):
    """Run a given SVN command in the specified working directory."""
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout


def get_local_current_revision(svn_path):
    """Get the current revision of the SVN repository."""
    command = ["svn", "info"]
    info_output = run_svn_command(command, cwd=svn_path)

    for line in info_output.splitlines():
        if line.startswith("Revision:"):
            return line.split()[1]
    return None


if __name__ == "__main__":
    # 设置本地 SVN 仓库路径
    local_svn_path = r"D:\test_svn"

    # 获取当前修订版本
    current_revision = get_local_current_revision(local_svn_path)

    if current_revision:
        print(f"Current SVN Revision: {current_revision}")
    else:
        print("Failed to retrieve the SVN revision.")
