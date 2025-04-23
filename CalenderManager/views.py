from celery.bin.worker import worker
from django.shortcuts import render
from ProjectManager.models import Task, Project, CheckList
from rest_framework import status
import jdatetime
from datetime import timedelta, date, datetime
from rest_framework.response import Response
from .serializers import *
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

class MeetingLabelManager(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,label_id=None):
        if label_id:
            label_obj = get_object_or_404(MeetingLabel,id=label_id)
            serializer_data = MeetingLabelSerializer(label_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })



        label_objs = MeetingLabel.objects.all()

        serializer_data = MeetingLabelSerializer(label_objs,many=True)
        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "موفق",
            "data": serializer_data.data
        })
    def post(self,request):

        serializer_data= MeetingLabelSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت ساخته شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.errors
        })
    def put(self,request,label_id):



        instance =get_object_or_404(MeetingLabel,id=label_id)
        serializer_data = MeetingLabelSerializer(instance=instance,data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت ساخته شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.errors
        })
    def delete(self,request,label_id):
        instance = get_object_or_404(MeetingLabel, id=label_id)
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class CalenderManger(APIView):
    permission_classes = [IsAuthenticated]

    def is_jalali_leap_year(self, year):
        """
        تعیین سال کبیسه در تقویم جلالی:
        """
        return year % 33 in {1, 5, 9, 13, 17, 22, 26, 30}

    def get_all_dates_of_month(self, year, month):
        start_date = jdatetime.date(year, month, 1)

        if month < 12:
            end_date = jdatetime.date(year, month + 1, 1) - jdatetime.timedelta(days=1)
        else:
            if self.is_jalali_leap_year(year):
                end_date = jdatetime.date(year, month, 30)
            else:
                end_date = jdatetime.date(year, month, 29)

        all_dates = [start_date + jdatetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        return all_dates

    def get_occurrences_in_month(self, schedule, year, month):
        """
        محاسبه تاریخ‌های وقوع برنامه (Schedule) در یک ماه مشخص بر اساس start_date و repeat_type.
        فرض می‌شود که start_date برنامه به میلادی ذخیره شده است.
        """
        try:
            start_date = schedule.date_to_start.date()
        except:
            return []
        month_start = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        month_end = date(year, month, last_day)

        occurrences = []
        repeat_type = schedule.reaped_type

        if repeat_type == "no_repetition":
            if month_start <= start_date <= month_end:
                occurrences.append(start_date)

        elif repeat_type == "daily":
            current = max(start_date, month_start)
            while current <= month_end:
                occurrences.append(current)
                current += timedelta(days=1)

        elif repeat_type == "weekly":
            current = start_date
            # اگر start_date قبل از ماه مورد نظر است، اولین وقوع در ماه را پیدا می‌کنیم.
            while current < month_start:
                current += timedelta(days=7)
            while current <= month_end:
                occurrences.append(current)
                current += timedelta(days=7)

        elif repeat_type == "monthly":
            # در هر ماه، اگر روز start_date معتبر باشد.
            if start_date.day <= last_day:
                occurrence = date(year, month, start_date.day)
                if occurrence >= start_date:
                    occurrences.append(occurrence)

        return occurrences

    def get(self, request):
        self.workspace_obj = get_object_or_404(WorkSpace, id=request.user.current_workspace_id)
        self.user = request.user
        command = request.GET.get("command")

        if command == "get_all_days":
            return self.handle_get_all_days(request)
        if command == "get_a_day":
            return self.handle_get_a_day(request)

        return Response({"status": False, "message": "Invalid command."},
                        status=status.HTTP_400_BAD_REQUEST)

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

        # دریافت لیست تمامی روزهای ماه به صورت jdatetime و لیست اولیه برای نمایش داده‌ها
        all_day_in_month = self.get_all_dates_of_month(year=year, month=month)
        data = self.get_list_data(month_list=all_day_in_month,request=request)



        return Response({"status": True, "message": "Success", "data": data},
                        status=status.HTTP_200_OK)

    def handle_get_a_day(self, request):
        """Handles the get_a_day command."""
        specific_date = request.GET.get("specific_date")
        if not specific_date:
            return Response({"status": False, "message": "specific_date is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # فرض شده فرمت تاریخ به شکل YYYY/MM/DD است.
            date_object = datetime.strptime(specific_date, "%Y/%m/%d").date()
        except ValueError:
            return Response({"status": False, "message": "Invalid date format. Use YYYY/MM/DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        check_list_objs = CheckList.objects.filter(
            task__project__workspace=self.workspace_obj,
            responsible_for_doing=self.user,
        )
        customer_objs = CustomerUser.objects.filter(
            workspace=self.workspace_obj,
            user_account=self.user
        )

        check_list_items = [
            item for item in check_list_objs
            if item.date_time_to_start_main and item.date_time_to_start_main.date() == date_object and not item.task.is_deleted
        ]
        customer_items = [
            customer for customer in customer_objs
            if customer.main_date_time_to_remember and customer.main_date_time_to_remember.date() == date_object and not customer.group_crm.is_deleted
        ]

        check_list_serializer = CheckListSerializer(check_list_items, many=True)
        customer_serializer = CustomerSmallSerializer(customer_items, many=True)

        # دریافت تمامی برنامه‌های موجود (می‌توانید بر اساس workspace فیلتر کنید)
        schedules = Meeting.objects.filter(workspace=self.workspace_obj,members__user=request.user)
        schedule_occurrences = []
        for schedule in schedules:
            occurrences = self.get_occurrences_in_month(schedule, date_object.year, date_object.month)
            if any(occ == date_object for occ in occurrences):
                schedule_occurrences.append(MeetingSerializer(schedule,context={'user': request.user}).data)

        response_data = {
            "task_list": check_list_serializer.data,
            "customer_list": customer_serializer.data,
            "schedule_occurrences": schedule_occurrences
        }

        return Response(
            {"status": True, "message": "موفق", "data": response_data},
            status=status.HTTP_200_OK,
        )

    def get_list_data(self, month_list,request):
        """Returns checklist count for each day in a month."""
        check_list_objs = CheckList.objects.filter(
            task__project__workspace=self.workspace_obj,
            responsible_for_doing=self.user,
        )
        customer_objs = CustomerUser.objects.filter(
            workspace=self.workspace_obj,
            user_account=self.user
        )

        data_list = []
        for jdate in month_list:
            g_date = jdate.togregorian()
            customer_list = [
                customer for customer in customer_objs
                if customer.main_date_time_to_remember and customer.main_date_time_to_remember.date() == g_date and not customer.group_crm.is_deleted
            ]
            check_list_items = [
                item for item in check_list_objs
                if item.date_time_to_start_main and item.date_time_to_start_main.date() == g_date and not item.task.is_deleted
            ]
            dic = {
                "date": jdate.strftime("%Y/%m/%d"),
                "count": len(customer_list) + len(check_list_items),
                "customer_list":CustomerSmallSerializer(customer_list,many=True).data,
                "task_list":CheckListSerializer(check_list_items,many=True).data,
                "schedule_occurrences":[]


            }
            schedules = Meeting.objects.filter(workspace=self.workspace_obj, members__user=request.user)

            for schedule in schedules:

                occurrences = self.get_occurrences_in_month(schedule, g_date.year, g_date.month)

                for occ in occurrences:

                    occ_str = occ.strftime("%Y/%m/%d")
                    # پیدا کردن روز مورد نظر در data (که شامل key "date" است)

                    if occ == g_date:
                            # اگر کلید schedule_occurrences موجود نیست، آن را به صورت لیست ایجاد می‌کنیم
                        dic['count'] += 1

                        dic['schedule_occurrences'].append(MeetingSerializer(schedule,context={'user': request.user}).data)
            data_list.append(dic)
        return data_list

    def post(self, request):
        print(request.data,"@@@")

        request.data['workspace_id'] = request.user.current_workspace_id
        serializer_data = MeetingSerializer(data=request.data, context={"user": request.user})
        if serializer_data.is_valid():
            meeting_obj =serializer_data.save()
            print(meeting_obj.remember_number,"!!!!")
            return Response(status=status.HTTP_201_CREATED, data={
                "status": True,
                "message": "با موفقیت ثبت شد",
                "data": serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "Validation Error",
            "data": serializer_data.errors
        })
    def put(self,request,meeting_id):
        instance = get_object_or_404(Meeting,id=meeting_id)
        request.data['workspace_id'] = instance.workspace.id
        serializer_data = MeetingSerializer(data=request.data,instance=instance, context={"user": request.user})
        if serializer_data.is_valid():
            meeting_obj =serializer_data.save()
            print(meeting_obj.remember_number,"!!!!")
            return Response(status=status.HTTP_202_ACCEPTED, data={
                "status": True,
                "message": "با موفقیت بروزرسانی شد",
                "data": serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "Validation Error",
            "data": serializer_data.errors
        })


    def delete(self,request,meeting_id):
        meeting_obj = get_object_or_404(Meeting,id=meeting_id)
        meeting_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_a_meeting(request,meeting_id):
    meeting_obj = get_object_or_404(Meeting,id=meeting_id)
    serializer_data = MeetingSerializer(meeting_obj)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"موفق",
        "data":serializer_data.data
    })
