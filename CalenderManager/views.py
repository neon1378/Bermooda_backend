from django.shortcuts import render
from ProjectManager.models import Task, Project, CheckList
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import date, datetime
import calendar
from ProjectManager.serializers import CheckListSerializer

# Create your views here.
class CalenderManger(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        year = request.GET.get("year")
        month = request.GET.get("month")

        if not year or not month:
            return Response(
                {"status": False, "message": "Year and month are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response(
                {"status": False, "message": "Year and month must be integers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = self.get_list_data(year, month)
        return Response(
            status=status.HTTP_200_OK,
            data={"status": True, "message": "success", "data": data}
        )

    def get_list_data(self, year: int, month: int):
        num_days = calendar.monthrange(year, month)[1]  # Get number of days in month
        data_list = []

        for day in range(1, num_days + 1):
            g_date = date(year, month, day)  # Create Gregorian date

            # Query checklist data based on Gregorian date
            check_list_objs = CheckList.objects.all()
            for item in check_list_objs:
                if item.date_time_to_start_main:
                    print(f"checklist_date : {item.date_time_to_start_main.date()}" )
                    print(f"month_date{g_date}")
                    print(item.date_time_to_start_main.date() ==g_date )

            data_list.append({
                "date": g_date.strftime("%Y-%m-%d"),  # Format Gregorian date as string
                "list":[]
            })

            print(f"Gregorian: {g_date}, Records found: {check_list_objs.count()}")

        return data_list
