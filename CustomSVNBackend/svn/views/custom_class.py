from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 200  # 每页显示的记录数，可以在此调整

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,  # 自定义返回值
            'page_count': self.page.paginator.num_pages,  # 自定义返回值
            'current_page': self.page.number,  # 自定义返回值
            'last_page': self.page.paginator.num_pages,  # 自定义返回值
            'results': data,
        })
