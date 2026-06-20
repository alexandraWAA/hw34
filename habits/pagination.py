from rest_framework.pagination import LimitOffsetPagination


class HabitPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 5
    limit_query_param = "limit"
    offset_query_param = "offset"
