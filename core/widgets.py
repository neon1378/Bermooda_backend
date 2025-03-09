
from django.core.paginator import Paginator
from rest_framework import status
import jdatetime
from datetime import datetime
from rest_framework.response import Response
class ReusablePaginationMixin:
    pagination_page_size = 20
    pagination_ordering = "-id"
    pagination_serializer_class = None
    pagination_data_key = "list"

    def get_paginated_response(self, queryset, page_number):
        # Configure pagination settings
        page_size = self.get_page_size()
        ordering = self.get_ordering()
        serializer_class = self.get_pagination_serializer_class()

        # Prepare ordered queryset
        ordered_queryset = queryset.order_by(ordering)
        paginator = Paginator(ordered_queryset, page_size)

        # Handle out-of-range pages
        if page_number > paginator.num_pages:
            return self.build_response(
                paginator=paginator,
                data=[],
                page_number=page_number
            )

        page = paginator.get_page(page_number)
        serializer = serializer_class(
            page.object_list,
            many=True,
            context=self.get_serializer_context()
        )

        # Process data through hook
        processed_data = self.process_paginated_data(serializer.data)

        return self.build_response(
            paginator=paginator,
            data=processed_data,
            page=page
        )

    # Configuration methods
    def get_page_size(self):
        return self.pagination_page_size

    def get_ordering(self):
        return self.pagination_ordering

    def get_pagination_serializer_class(self):
        return self.pagination_serializer_class or self.get_serializer_class()

    # Response construction
    def build_response(self, paginator, data, page=None, page_number=None):
        response_data = {
            "status":True,
            "message":"با موفقیت انجام شد",
            "data":{
                "count": paginator.count,
                "next": None,
                "previous": None,
                self.pagination_data_key: data
            }

        }

        if page:
            response_data["next"] = page.next_page_number() if page.has_next() else None
            response_data["previous"] = page.previous_page_number() if page.has_previous() else None
        elif page_number:
            response_data["next"] = None if page_number >= paginator.num_pages else page_number + 1
            response_data["previous"] = page_number - 1 if page_number > 1 else None

        return Response(status=status.HTTP_200_OK,data =response_data)

    # Override hook for data processing
    def process_paginated_data(self, data):
        """
        Override this method to modify paginated data before final response
        Example usage: Add user-specific flags to serialized data
        """
        return




import jdatetime
from datetime import datetime
from django.utils.timezone import make_aware

def persian_to_gregorian(persian_date_str):
    """
    تبدیل رشته تاریخ شمسی به شیء datetime میلادی.
    اگر رشته نال باشد یا فرمت اشتباه داشته باشد، None برمی‌گرداند.
    """
    if not persian_date_str:
        return None

    try:
        # اگر زمان وجود داشته باشد (فرمت کامل تاریخ و زمان)
        if len(persian_date_str) > 10:
            persian_datetime = datetime.strptime(persian_date_str, "%Y/%m/%d %H:%M")
            year, month, day = persian_datetime.year, persian_datetime.month, persian_datetime.day
            hour, minute = persian_datetime.hour, persian_datetime.minute
        else:
            # اگر فقط تاریخ باشد (بدون زمان)
            persian_datetime = datetime.strptime(persian_date_str, "%Y/%m/%d")
            year, month, day = persian_datetime.year, persian_datetime.month, persian_datetime.day
            hour, minute = 0, 0  # زمان پیش‌فرض

        # تبدیل تاریخ شمسی به میلادی
        gregorian_date = jdatetime.date(year, month, day).togregorian()

        # ایجاد شیء datetime با زمان
        datetime_obj = datetime(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day,
            hour,
            minute,

        )

        # اگر از timezone استفاده می‌کنید، آن را aware کنید
        return make_aware(datetime_obj)

    except ValueError:
        # اگر فرمت رشته اشتباه باشد
        return None

