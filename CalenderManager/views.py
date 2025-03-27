from django.shortcuts import render
from ProjectManager.models import Task, Project, CheckList
from rest_framework import status
import jdatetime
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import date, datetime
import calendar
from WorkSpaceManager.models import WorkSpace

from ProjectManager.serializers import CheckListSerializer
from django.shortcuts import get_object_or_404
from CrmCore.serializers import CustomerSmallSerializer
from CrmCore.models import CustomerUser
class CalenderManger(APIView):

    permission_classes=[IsAuthenticated]

    def is_jalali_leap_year(self,year):
        """
        Determine if a Jalali year is a leap year.
        Leap years in the Jalali calendar occur in years where:
        year % 33 is in [1, 5, 9, 13, 17, 22, 26, 30].
        """
        return year % 33 in {1, 5, 9, 13, 17, 22, 26, 30}

    def get_all_dates_of_month(self, year, month):
        start_date = jdatetime.date(year, month, 1)

        if month < 12:
            # For months other than Esfand (month 12), the end date is the last day of the month
            end_date = jdatetime.date(year, month + 1, 1) - jdatetime.timedelta(days=1)
        else:
            # For Esfand (month 12), check if it's a leap year using the custom function
            if self.is_jalali_leap_year(year):  # Use custom leap year function
                end_date = jdatetime.date(year, month, 30)  # 30 days in Esfand for leap years
            else:
                end_date = jdatetime.date(year, month, 29)  # 29 days in Esfand for non-leap years

        # Generate all dates in the month
        all_dates = [start_date + jdatetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        return all_dates

    def get(self, request, date=None):
        self.workspace_obj = get_object_or_404(WorkSpace, id=request.user.current_workspace_id)
        self.user = request.user
        command = request.GET.get("command")

        if command == "get_all_days":
            return self.handle_get_all_days(request)

        if command == "get_a_day":
            return self.handle_get_a_day(request)

        return Response({"status": False, "message": "Invalid command."}, status=status.HTTP_400_BAD_REQUEST)

    def handle_get_all_days(self, request):
        """Handles the get_all_days command."""
        year = request.GET.get("year")
        month = request.GET.get("month")

        if not year or not month:
            return Response({"status": False, "message": "Year and month are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            year, month = int(year), int(month)
        except ValueError:
            return Response({"status": False, "message": "Year and month must be integers."},
                            status=status.HTTP_400_BAD_REQUEST)


        all_day_in_month =  self.get_all_dates_of_month(year=year, month=month)
        data = self.get_list_data(moth_list=all_day_in_month)
        return Response({"status": True, "message": "Success", "data": data}, status=status.HTTP_200_OK)

    def handle_get_a_day(self, request):
        """Handles the get_a_day command."""
        specific_date = request.GET.get("specific_date")

        if not specific_date:
            return Response({"status": False, "message": "specific_date is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            date_object = datetime.strptime(specific_date, "%Y/%m/%d").date()
        except ValueError:
            return Response({"status": False, "message": "Invalid date format. Use YYYY/MM/DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        check_list_objs = CheckList.objects.filter(
            task__project__workspace=self.workspace_obj,
            responsible_for_doing=self.user,

        )
        customer_objs = CustomerUser.objects.filter(
            workspace =self.workspace_obj,
            user_account = self.user

        )
        check_list_items =[]
        for check_list in check_list_items:

            if check_list.date_time_to_start_main and check_list.date_time_to_start_main.date()==date_object:
                check_list_items.append(check_list)

        customer_items = []
        for customer in customer_objs:
            if customer.main_date_time_to_remember and customer.main_date_time_to_remember.date() == date_object:
                customer_items.append(customer)
        check_list_serializer = CheckListSerializer(check_list_items, many=True)
        customer_serializer  =CustomerSmallSerializer(customer_items,many=True)
        return Response(
            {
                "status": True,
                "message": "موفق",
                "data": {
                    "task_list":check_list_serializer.data,
                    "customer_list":customer_serializer.data
                },
            },
            status=status.HTTP_200_OK,
        )

    def get_list_data(self,month_list):
        """Returns checklist count for each day in a month."""

        check_list_objs = CheckList.objects.filter(
            task__project__workspace=self.workspace_obj,
            responsible_for_doing=self.user,

        )

        customer_objs = CustomerUser.objects.filter(
            workspace =self.workspace_obj,
            user_account = self.user

        )

        data_list = []
        for jdate in month_list:
            g_date = jdate.togregorian()

            customer_list = [
                customer for customer in customer_objs
                if customer.main_date_time_to_remember and customer.main_date_time_to_remember.date() == g_date
            ]

            check_list_items = [
                item for item in check_list_objs
                if item.date_time_to_start_main and item.date_time_to_start_main.date() == g_date
            ]

            data_list.append({
                "date": jdate.strftime("%Y/%m/%d"),
                "count": len(customer_list) + len(check_list_items)
            })

        return data_list