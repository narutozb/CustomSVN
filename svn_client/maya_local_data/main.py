from maya_local_data.utils import get_svn_file_info

svn_local_dir = r"D:\test_svn"
li = get_svn_file_info(svn_local_dir)
for i in li:
    print(i)
