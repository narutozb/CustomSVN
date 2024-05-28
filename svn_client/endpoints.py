class Endpoints:
    ROOT_URL = 'http://127.0.0.1:8000'
    COMMITS = '/api/commits/'

    @classmethod
    def get_url(cls, endpoint):
        '''
        获取完整的URL
        :param endpoint:
        :return:
        '''
        return cls.ROOT_URL + endpoint
