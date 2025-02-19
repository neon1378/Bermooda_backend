from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import *
from core.permission import IsWorkSpaceUser
from django.shortcuts import get_object_or_404
import jdatetime
from Notification.models import Notification
from Notification.views import create_notification
from django.db.models import Q
# Create your views here.

class PlaningManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceUser]
    
    def get_all_dates_of_month(self,year, month):
        
        start_date = jdatetime.date(year, month, 1)
        
        
        if month < 12:
        
            end_date = jdatetime.date(year, month + 1, 1) - jdatetime.timedelta(days=1)
        else:
        
            end_date = jdatetime.date(year, month, 29) if not jdatetime.date.isleap(year) else jdatetime.date(year, month, 30)
        
        
        all_dates = [start_date + jdatetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        
        return all_dates
    def get(self, request, plan_id=None):
        if plan_id:
            return self._get_plan_details(plan_id)

        data = request.data
        workspace_id = request.GET.get("workspace_id")
        month = int(request.GET.get('month'))
        year = int(request.GET.get("year"))

        planing_objs = Planing.objects.filter(
            Q(workspace_id=workspace_id),
            Q(creator=request.user) | Q(invited_users__id=request.user.id)
        ).distinct()

        response_date = []
        for plan in planing_objs:
            if self._is_plan_activated(plan, request.user):
                response_date.extend(self._process_plan_dates(plan, year, month))

        return Response(
            status=status.HTTP_200_OK,
            data={"status": True, "message": "success", "data": response_date},
        )

    def _get_plan_details(self, plan_id):
        plan_obj = get_object_or_404(Planing, id=plan_id)
        serializer_data = PlaningSerializer(plan_obj)
        return Response(
            status=status.HTTP_200_OK,
            data={
                "status": True,
                "message": "success",
                "data": serializer_data.data,
            },
        )

    def _is_plan_activated(self, plan, user):
        if InvitedUser.objects.filter(user=user, planing=plan).exists():
            invited_user = InvitedUser.objects.get(user=user, planing=plan)
            return invited_user.activated or plan.creator == user
        return True

    def _process_plan_dates(self, plan, year, month):
        response_date = []
        try:
            date_in_calender = jdatetime.date(*map(int, plan.date_in_calender.split('/')))
        except:
            date_in_calender = jdatetime.date(*map(int, "1410/10/10".split('/')))

        if plan.reaped_status:
            response_date.extend(self._handle_reaped_status(plan, date_in_calender, year, month))
        else:
            if date_in_calender.year == year and date_in_calender.month == month:
                response_date.append(self._create_response(plan, date_in_calender, reaped_status=False))

        return response_date

    def _handle_reaped_status(self, plan, date_in_calender, year, month):
        response_date = []


        if   date_in_calender.year <= year and (date_in_calender.month <= month or date_in_calender.year < year ):
            
            if plan.range_date:
                if plan.range_date.reaped_type == "weekly":
                    response_date.extend(self._generate_dates(plan, date_in_calender, 7))
                elif plan.range_date.reaped_type == "daily":
                    response_date.extend(self._generate_dates(plan, date_in_calender, 1))
                if plan.range_date.reaped_type == "monthly":
                    next_month_same_day = self._calculate_next_month_date(date_in_calender)
                    response_date.append(self._create_response(plan, next_month_same_day))

            return response_date

    def _generate_dates(self, plan, start_date, step):
        dates = []
        end_of_month = self._calculate_end_of_month(start_date)
        current_date = start_date

        while current_date <= end_of_month:
            dates.append(self._create_response(plan, current_date))
            current_date += jdatetime.timedelta(days=step)

        return dates

    def _calculate_end_of_month(self, date):
        if date.month < 12:
            return jdatetime.date(date.year, date.month + 1, 1) 
        return jdatetime.date(date.year + 1, 1, 1) - jdatetime.timedelta(days=1)

    def _calculate_next_month_date(self, date):
        if date.month < 12:
            return jdatetime.date(date.year, date.month + 1, date.day)
        return jdatetime.date(date.year + 1, 1, date.day)

    def _create_response(self, plan, date, reaped_status=True):
        return {
            "date": date.day,
            "plan_id": plan.id,
            "title": plan.title,
            "label_title": plan.label_title,
            "label_color_code": plan.label_color_code,
            "reaped_type":plan.range_date.reaped_type if plan.reaped_status else None,
            "reaped_status": reaped_status,
        }


    def post(self,request):
        request.data['creator_id'] = request.user.id
        workspace_id = request.data['workspace_id']
        serializer_data = PlaningSerializer(data=request.data)
        if serializer_data.is_valid():
            plan_obj = serializer_data.save()
            for user in plan_obj.invited_users.all():
                sub_title= f"برنامه {plan_obj.title} توسط {plan_obj.creator.fullname} برای شما برنامه ریزی شد"
                title= "برنامه ریزی"
                create_notification(related_instance=plan_obj,workspace=WorkSpace.objects.get(id=workspace_id),user=user.user,title=title,sub_title=sub_title,side_type="invite_plan")
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":serializer_data.errors
        })
    


   
    def put (self,request,plan_id):
        
        plan_obj = get_object_or_404(Planing,id=plan_id)
        if plan_obj.creator == request.user:

            serializer_data = PlaningSerializer(data=request.data,instance=plan_obj)
            if serializer_data.is_valid():
                serializer_data.save()
                return Response(status=status.HTTP_202_ACCEPTED,data = {
                    "status":True,
                    "message":"success",
                    "data":serializer_data.data
                })
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"errors",
                "data":serializer_data.errors
            })
        else :
            return Response(status=status.HTTP_403_FORBIDDEN,data={
                "status":False,
                "message":"Access Denied",
                "data":{}
            })



    def delete(self,request,plan_id):
        plan_obj = get_object_or_404(Planing,id=plan_id)
        plan_obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsWorkSpaceUser ])
def accept_or_deny_plan(request):
    data= request.data
    plan_id= data.get("plan_id")
    workspace_id = data.get('workspace_id')
    notif_id = data.get("notif_id")
    accepted= data.get("accepted")
    plan_obj = get_object_or_404(Planing,id= plan_id)
    notif_obj = get_object_or_404(Notification,id=notif_id)
    if accepted: 
        sub_title= f"{request.user.fullname} درخواست دعوت به برنامه ریزی شما رو قبول کرد"
        title= "برنامه ریزی"
        create_notification(related_instance=plan_obj,workspace=WorkSpace.objects.get(id=workspace_id),user=plan_obj.creator,title=title,sub_title=sub_title,side_type="accept_invite")

        for user_invited in plan_obj.invited_users.all():
            if user_invited.user == request.user:
                user_invited.activated=True
                user_invited.save()
        notif_obj.delete()
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"برنامه به تقویم شما اضافه  شد",
            "data":{}
        })
    else:
        sub_title= f"{request.user.fullname} درخواست دعوت به برنامه ریزی {plan_obj.title}  رو رد  کرد"
        title= "برنامه ریزی"
        create_notification(related_instance=plan_obj,workspace=WorkSpace.objects.get(id=workspace_id),user=plan_obj.creator,title=title,sub_title=sub_title,side_type="deny_invite")
        for user_invited in plan_obj.invited_users.all():
            if user_invited.user == request.user:
                user_invited.delete()
        print(notif_obj)
        notif_obj.delete()
        print(notif_obj)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"برنامه رد شد",
            "data":{}
        })