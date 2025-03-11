from django.shortcuts import render
from ProjectManager.models import Task,Project,CheckList
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import  APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
# Create your views here.


# class CalenderManger(APIView):
#     def get(self,request):
#
#
#
#         command = request.GET.get("command")
#
# #         command=  "get_month_data"
# #         command = "get_day_data"
#         if command == "get_month_data":
#             # main_data=






    # data = {"command": "get_month_data",
    #         "data": {
    #         "year": "1403",
    #         "month": "05",
    #     }}
    # data = {"command": "get_day_data",
    #         "data": {
    #         "year": "1403",
    #         "month": "05",
    #         "day":"01"
    #     }}