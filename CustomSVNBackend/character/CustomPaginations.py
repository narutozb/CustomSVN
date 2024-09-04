from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    # 设置默认每页的数量
    page_size = 100
    # 允许客户端通过查询参数控制每页的大小
    page_size_query_param = 'page_size'
    # 设置允许的最大每页数量
    max_page_size = 500

    # 重写 get_paginated_response 方法来自定义响应结构
    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'total_items': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'results': data
        })
