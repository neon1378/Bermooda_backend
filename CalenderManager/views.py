from django.shortcuts import render
from ProjectManager.models import Task, Project, CheckList
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import date, datetime
import calendar
from WorkSpaceManager.models import WorkSpace

from ProjectManager.serializers import CheckListSerializer
from django.shortcuts import get_object_or_404


class CalenderManger(APIView):
    permission_classes=[IsAuthenticated]
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

        data = self.get_list_data(year, month)
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
            date_time_to_start_main__date=date_object
        )

        serializer = CheckListSerializer(check_list_objs, many=True)
        return Response(
            {
                "status": True,
                "message": "موفق",
                "data": {"data_type": "check_list", "list": serializer.data},
            },
            status=status.HTTP_200_OK,
        )

    def get_list_data(self, year: int, month: int):
        """Returns checklist count for each day in a month."""
        num_days = calendar.monthrange(year, month)[1]  # Get number of days in month
        data_list = []

        check_list_objs = CheckList.objects.filter(
            task__project__workspace=self.workspace_obj,
            responsible_for_doing=self.user,
            date_time_to_start_main__year=year,
            date_time_to_start_main__month=month
        )

        for day in range(1, num_days + 1):
            g_date = date(year, month, day)  # Create Gregorian date

            # Filter only checklists for this specific day
            count = check_list_objs.filter(date_time_to_start_main__day=day).count()

            data_list.append({
                "date": g_date.strftime("%Y/%m/%d"),
                "count": count
            })