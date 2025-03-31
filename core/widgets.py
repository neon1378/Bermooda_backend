from traceback import print_tb

from django.core.paginator import Paginator
from rest_framework import status
import jdatetime
from django.utils.timezone import is_aware, make_naive
from dotenv import load_dotenv
load_dotenv()
import os
import locale
from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests

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


def convert_persian_to_latin_numbers(persian_str):
    persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
    latin_numbers = "0123456789"
    translation_table = str.maketrans(persian_numbers, latin_numbers)
    return persian_str.translate(translation_table)


def persian_to_gregorian(persian_date_str):
    try:
        if not persian_date_str:
            return None

        persian_date_str = convert_persian_to_latin_numbers(persian_date_str.strip())

        if len(persian_date_str) > 10:
            # If date includes time
            persian_datetime = jdatetime.datetime.strptime(persian_date_str, "%Y/%m/%d %H:%M")
            year, month, day = persian_datetime.year, persian_datetime.month, persian_datetime.day
            hour, minute = persian_datetime.hour, persian_datetime.minute
        else:
            # Only date
            year, month, day = map(int, persian_date_str.split('/'))
            hour, minute = 0, 0

        # Convert Persian date to Gregorian
        gregorian_date = jdatetime.date(year, month, day).togregorian()

        datetime_obj = datetime(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day,
            hour,
            minute,
        )

        # Convert to naive datetime if USE_TZ=False
        if is_aware(datetime_obj):
            return make_naive(datetime_obj)
        else:
            return datetime_obj
    except ValueError:
        return None


def change_current_workspace_jadoo(user_acc,workspace_obj):
        try:
            jadoo_base_url =os.getenv("JADOO_BASE_URL")
            url = f"{jadoo_base_url}/workspace/changeWorkSpace"
            headers = {
                "content-type": "application/json",
                "Authorization": f"Bearer {user_acc.refrence_token}"

            }
            payload = {
                "workspaceId":workspace_obj.jadoo_workspace_id
            }
            print(payload)
            response = requests.post(url=url,json=payload,headers=headers)
            print(response)
        except:
            pass




def gregorian_to_persian(date_time,type=None):
    locale.setlocale(locale.LC_ALL, 'fa_IR')
    if type == "date_time":
        jalali_date = jdatetime.datetime.fromgregorian(datetime=date_time)
        formatted_date_persian = jalali_date.strftime("%d %B %Y | %H:%M ")
        return formatted_date_persian
    else:

        jalali_date = jdatetime.datetime.fromgregorian(datetime=date_time)
        formatted_date_persian = jalali_date.strftime("%d %B %Y")
        return formatted_date_persian




def pagination (query_set,page_number):




        paginator = Paginator(query_set, 20)  # Set items per page

        # Check if the requested page exists
        if int(page_number) > paginator.num_pages:
            return {

                "count": paginator.count,
                "next": None,
                "previous": None,
                "list": []
            }

        # Get the page
        page = paginator.get_page(page_number)





        # Group messages by date



        return {
            "count": paginator.count,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": page.object_list
        }

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')  # Get direct IP if no proxy
    return ip



# upload_handlers.py


class ProgressBarUploadHandler(FileUploadHandler):
    """
    Custom upload handler to track file upload progress and send updates via Channels.
    """
    def __init__(self, request=None):
        super().__init__(request)
        # Expect the client to pass an 'upload_id' as a GET parameter.
        self.upload_id = request.GET.get('upload_id')
        self.content_length = int(request.META.get('CONTENT_LENGTH', 0))

        self.content_length_main = int(request.headers.get("CONTENT_LENGTH",0))

        self.uploaded_bytes = 0
        self.channel_layer = get_channel_layer()
        if self.upload_id:
            cache.set(self.upload_id, 0, timeout=60*60)

    def receive_data_chunk(self, raw_data, start):
        self.uploaded_bytes += len(raw_data)

        if self.upload_id and self.content_length_main:
            print("yess")
            progress = int((self.uploaded_bytes / self.content_length_main) * 100)
            cache.set(self.upload_id, progress, timeout=60*60)
            async_to_sync(self.channel_layer.group_send)(
                self.upload_id,
                {
                    "type": "upload_progress",  # This method will be called in the consumer.
                    "progress": progress,
                }
            )
        return raw_data

    def file_complete(self, file_size):
        return None
