from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 50

    def get_page_size(self, request):
        # Get the requested page size from the query parameters
        page_size = request.query_params.get('size', self.page_size)

        # Ensure that the requested page size is not greater than the max page size
        return min(int(page_size), self.max_page_size)

    def get_paginated_response(self, data):

        return Response({
            'data_count': len(data),
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'total_pages': self.page.paginator.num_pages,
            'data': data,
            "message":"list data retrive successfully."
        })