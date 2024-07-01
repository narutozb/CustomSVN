from config import Config
from svn_utils import get_svn_log, parse_svn_log

current_start_revision = 1
current_end_revision = 10

log_data = get_svn_log(Config.LOCAL_REPO_URL, start_revision=current_start_revision, end_revision=current_end_revision)

print(log_data)

commits = parse_svn_log(log_data)

print(len(commits))
