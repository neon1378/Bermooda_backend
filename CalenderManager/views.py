from logging import setLogRecordFactory

from django.shortcuts import render
from ProjectManager.models import Task,Project,CheckList
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import  APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
import jdatetime
from datetime import date
from rest_framework.permissions import AllowAny
from ProjectManager.models import  CheckList
from ProjectManager.serializers import CheckListSerializer
# Create your views here.


class CalenderManger(APIView):
    permission_classes= [AllowAny]
    def jalali_days_in_month(self,year: int, month: int) -> int:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")
        if month <= 6:
            return 31
        elif month <= 11:
            return 30
        else:  # month == 12
            # Create a dummy date for the first day of the month to check for leap year
            dummy = jdatetime.date(year, month, 1)
            return 30 if dummy.isleap() else 29
    def get(self,request):
        year = request.GET.get("year")
        month = request.GET.get("month")
        data =self.get_list_data(j_year=int(year),j_month=int(month))
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":data
        })
    def get_list_data(self,j_year: int, j_month: int):
        num_days =self.jalali_days_in_month(j_year, j_month)
        data_list = []
        for day in range(1, num_days + 1):
            # Create the Jalali date
            j_date = jdatetime.date(j_year, j_month, day)
            # Convert to Gregorian date
            g_date: date = j_date.togregorian()
            check_list_objs = CheckList.objects.filter(date_time_to_start_main__date =g_date)
            data_list.append(
                {
                    "date":j_date.strftime("%Y/%m/%d"),
                    "list":[
                        CheckListSerializer(check_list_objs,many=True).data

                    ]
                }
            )

            print(f"Jalali: {j_date}, Gregorian: {g_date}, Records found: ")

        return data_list