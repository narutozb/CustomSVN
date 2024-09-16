from config import Config


class Endpoints:
    '''
    APP_ENDPOINT = ''
    '''
    root_url = Config.ROOT_URL
    api_url = f'{root_url}/api/'
    token_auth = 'user/login/'  # 验证用户

    maya_sceneinfos = 'maya/mayafilesview/'  # 上传maya数据

    # FBX API
    receive_fbx_file = 'fbx/receive_fbx_file_data/'  # 接收并储存fbx_file数据

    @classmethod
    def get_api_url(cls, endpoint, print_url=False):
        '''
        获取完整的URL
        :param print_url:
        :param endpoint:
        :return:
        '''
        result = cls.api_url + endpoint
        if print_url:
            print(result)
        return result
