from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 100  # 默认值设为100
    page_size_query_param = 'page_size'  # 允许客户端通过查询参数设置页面大小
    max_page_size = 1000  # 设置最大页面大小，防止过大的请求

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.get_page_size(self.request),
            'page_count': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'last_page': self.page.paginator.num_pages,
            'results': data,
        })

    def get_empty_paginated_response(self, message):
        return Response({
            'count': 0,
            'next': None,
            'previous': None,
            'page_size': self.page_size,
            'page_count': 0,
            'current_page': 1,
            'last_page': 0,
            'results': [],
            'message': message
        })