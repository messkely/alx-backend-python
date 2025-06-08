from rest_framework import pagination
from rest_framework.response import Response


class MessagePagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'  # Optional: allows client to override
    max_page_size = 100  # Optional: limits max override

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total_messages': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })
