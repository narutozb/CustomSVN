import base64
import json
import subprocess

from settings import MayaClientSettings


def encode_arg(arg):
    # 将字符串编码为字节，并使用base64编码以确保字节内容可以作为命令行参数传递
    return base64.b64encode(arg.encode('utf-8')).decode('ascii')


def get_maya_data(maya_file_path):
    '''
    通过传输maya文件路径给mayaapp处理，将结果保存在特定路径，并将路径传回，最后获取json数据
    :param maya_file_path:
    :return:
    '''
    script_path = MayaClientSettings.data.get('MAYAAPP').get('get_data_maya_data').get('path')
    commands = [MayaClientSettings.get_maya_interpreter_path(), script_path, maya_file_path, ]
    print(commands)
    # 调用b.py并传递参数
    result = subprocess.run(
        commands,  # 使用Maya的python解释器运行脚本
        capture_output=True,
        text=True,
        encoding='utf-8',
    )

    # 获取b.py的输出
    output = result.stdout.strip()
    # 解析输出，提取需要的结果
    for line in output.splitlines():
        print('---' + line)
        if "MAYAAPP_RESULT:" in line:  # 假设返回的结果标识为 "Result:"
            return line.split("MAYAAPP_RESULT:")[-1].strip()
    return None


class MayaData:
    def __init__(self):
        pass

    def get_data(self, path) -> list[dict]:
        # path = r'D:\svn_project_test\MyDataSVN_trunk\RootFolder\test_file1 - 副本 - 副本 (2).mb'
        result = get_maya_data(encode_arg(path), )
        with open(str(result), 'r', encoding='utf8') as f:
            return json.loads(f.read())


if __name__ == '__main__':
    print(MayaData().get_data())
