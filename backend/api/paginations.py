from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пользовательский класс, позволяет осуществлять пагинацию
    списка пользователей и списка рецептов с использованием в
    запросе параметров номера страницы и лимита."""

    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 30
