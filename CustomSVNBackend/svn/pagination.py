from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 500  # 每页显示的记录数，可以在此调整

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count if hasattr(self, 'page') else 0,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'page_count': self.page.paginator.num_pages if hasattr(self, 'page') else 0,
            'current_page': self.page.number if hasattr(self, 'page') else 1,
            'last_page': self.page.paginator.num_pages if hasattr(self, 'page') else 0,
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