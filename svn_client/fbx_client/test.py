import os

from fbx_client.fbx_tools.custom_layer import CustomLayer
from fbx_client.fbx_tools.reader import CustomFbxReader
from svn_utils import get_local_current_revision, get_local_file_svn_info

root_dir = r'D:\svn_project_test\MyDataSVN\trunk\RootFolder'


def get_fbx_paths(root_dir: str):
    result: list[str] = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.fbx'):
                result.append(os.path.join(root, file))
    return result



fbx_path_list = get_fbx_paths(root_dir)

reader = CustomFbxReader()

file_path = fbx_path_list[0]
print(get_local_file_svn_info(file_path))

# reader.load_scene(file_path=file_path)
# takes = CustomLayer.get_all_takes_custom_data(reader.scene)
# for i in takes:
#     print(i)
