"""Pagination classes used across the API."""

from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    """
    Default paginator — page number based.
    Supports ?page=N&page_size=N
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "pagination": {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page_size": self.get_page_size(self.request),
            },
            "results": data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "pagination": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                        "total_pages": {"type": "integer"},
                        "current_page": {"type": "integer"},
                        "next": {"type": "string", "nullable": True},
                        "previous": {"type": "string", "nullable": True},
                        "page_size": {"type": "integer"},
                    },
                },
                "results": schema,
            },
        }


class CursorResultsPagination(CursorPagination):
    """
    Cursor-based paginator — for large datasets and real-time feeds.
    More efficient than page-number for millions of rows.
    Supports ?cursor=<encoded_cursor>
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"

    def get_paginated_response(self, data):
        return Response({
            "pagination": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page_size": self.get_page_size(self.request),
            },
            "results": data,
        })


class LargeResultsPagination(PageNumberPagination):
    """For admin exports — larger page sizes allowed."""
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000
