from django.core.paginator import Paginator, Page


class PaginatorUtil:
    @staticmethod
    def get_page_info(current_page: int, object_list, per_page: int):
        paginator = Paginator(object_list=object_list, per_page=per_page)
        total_page_info: Page = paginator.get_page(number=current_page)
        total_pages = total_page_info.paginator.num_pages

        current_page = total_page_info.number
        object_list = total_page_info.object_list
        return object_list, total_pages, current_page
