from django.shortcuts import render
from rest_framework import status 
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .models import Notification
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from firebase_admin import messaging
from UserManager.models import UserAccount,FcmToken
from rest_framework.permissions import IsAuthenticated
from WorkSpaceManager.models import WorkSpace,WorkspaceMember
from django.shortcuts import get_object_or_404
from core.widgets import pagination
import json
# Create your views here.


def send_notification_to_device(title,custom_data, body,fcm_token):
        try:
            # Create a message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=fcm_token,
                data=custom_data
            )
            # Send the message
            response = messaging.send(message)
            print(f"Successfully sent notification: {response}")
        except Exception as e:
            print(f"Error sending notification: {e}")

@api_view(['GET'])
@permission_classes([AllowAny])
def test_notif (request):
    device_name = request.data.get('device_name', 'Unnamed Device')
    print(device_name)
    # try:
    #         # Create a message
    #         message = messaging.Message(
    #             notification=messaging.Notification(
    #                 title="title",
    #                 body="body",
    #             ),
    #             token="cU_PKqFxQwuskCcmZVudi0:APA91bHd0B7J0ogXxkRaMgEdD0AUQ1oMPwmZqhl-PXx1ZoQC2Au7_pw0YrSYecHsGVunaQSdu0hpJVRdNSF0-rGRGaUYxl5s5JhVLK4vO1xESwKJ2MJo5Q4",
    #             data={
    #                   "id":"fuck"
    #             } 
    #         )
    #         # Send the message
    #         response = messaging.send(message)
    #         print(f"Successfully sent notification: {response}")
    # except Exception as e:
    #         print(f"Error sending notification: {e}")
    #         return Response(status=status.HTTP_200_OK) 
    return Response(status=status.HTTP_200_OK) 



def notif_data (notification_obj,workspace_obj=None,side_type=None,user=None):

        object_name = notification_obj.related_object.__class__.__name__
        dic ={}
        try:
            if object_name == "Task":
                    task_obj = notification_obj.related_object
                    dic['data_type'] = "project_task"
                    dic['side_type'] =notification_obj.side_type
                    try:
                        dic['department_id'] = str(task_obj.project.department.id)
                    except:
                        dic['department_id']=None
                    dic['task_id'] = str(task_obj.id)
                    dic['category_id'] = str(task_obj.category_task.id)
                    dic['project_id'] = str(task_obj.project.id)

                    dic['workspace_id'] = str(workspace_obj.id)
            elif object_name == "Report":
                    report_obj= notification_obj.related_object
                    dic['data_type'] = "crm_report"
                    dic['side_type'] = notification_obj.side_type
                    dic['report_id'] = str(report_obj.id)
                    dic['workspace_id'] = str(workspace_obj.id)
                    customer_obj = None
                    customer_obj = next(iter(report_obj.customer_user.all()), None)

                    dic['customer_id'] = str(customer_obj.id)
                    dic['group_id'] = str(customer_obj.group_crm.id)
                    dic['workspace_id'] = str(workspace_obj.id)
            elif object_name == "Planing":
                    plan_obj=notification_obj.related_object
                    dic['data_type'] = "plan_member"
                    dic['side_type'] = notification_obj.side_type
                    dic['plan_id'] = str(plan_obj.id)
                    dic['workspace_id'] = str(workspace_obj.id)

            elif object_name == "Mail":
                mail_obj = notification_obj.related_object
                dic['data_type'] = "mail_manager"
                dic['side_type'] = notification_obj.side_type
                dic['mail_id'] = str(mail_obj.id)
                dic['workspace_id'] = str(workspace_obj.id)
            elif object_name == "WorkspaceMember":
                member_obj =   notification_obj.related_object
                dic['data_type'] = "member_manager"
                dic['side_type'] = notification_obj.side_type
                dic['member_id'] = member_obj.id
                if member_obj.user_account.current_workspace_id not in (0, None):
                    dic['workspace_id'] = member_obj.user_account.current_workspace_id
                # if workspace_obj:
                    #  dic['workspace_id']= workspace_obj.id
            elif object_name == "CheckList":
                check_list_obj = notification_obj.related_object
                dic['data_type'] = "task_chek_list"
                dic['side_type'] = notification_obj.side_type
                try:
                    dic['department_id'] = str(check_list_obj.task.project.department.id)
                except:
                    dic['department_id'] = None
                dic['check_list_id'] = str(check_list_obj.id)
                dic['task_id'] = str(check_list_obj.task.id)
                dic['category_id'] = str(check_list_obj.task.category_task.id)
                dic['project_id'] = str(check_list_obj.task.project.id)

                dic['workspace_id'] = str(workspace_obj.id)
            elif object_name == "CustomerUser" :
                customer_obj = notification_obj.related_object
                dic['data_type'] = "customer"
                dic['side_type'] = notification_obj.side_type
                try:
                    dic['department_id'] = str(customer_obj.group_crm.department.id)
                except:
                    dic['department_id'] = None
                dic['customer_id'] = str(customer_obj.id)
                dic['group_crm_id'] = str(customer_obj.group_crm.id)
                dic['label_id'] = str(customer_obj.label.id)


                dic['workspace_id'] = str(workspace_obj.id)

        except:
            pass
        return dic
def create_notification (related_instance,workspace=None,user=None,title=None,sub_title=None,side_type=None):
    content_type = ContentType.objects.get_for_model(related_instance.__class__)
    notif_object =Notification.objects.create(
        title=title,
        sub_title=sub_title,
        user_account=user,
        content_type=content_type,
        object_id=related_instance.id,
        workspace=workspace,
        side_type=side_type,
        



    )
    custom_data = notif_data(notification_obj=notif_object,workspace_obj=workspace,side_type=side_type,user=user)
    
    print(custom_data)

    for fcm_token in FcmToken.objects.filter(user_account=user):
        # if not fcm_token.is_application:
        print(send_notification_to_device(title=title,body=sub_title,fcm_token=fcm_token.token,custom_data=custom_data))
    

    

class NotifacticatonManager(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        
        workspace_id = request.user.current_workspace_id
        is_paginate = request.GET.get("is_paginate",False)
        page_number = request.GET.get("page_number",1)
        per_page_count = request.GET.get("per_page_count",20)

        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        all_notifications = Notification.objects.filter(user_account=request.user,is_read=False).order_by("-created")
        if not is_paginate:
            notification_objs= Notification.objects.filter(user_account=request.user).order_by("-created")
        else:
            notification_data =Notification.objects.filter(user_account=request.user).order_by("-created")
            notification_objs = pagination(query_set=notification_data,page_number=page_number,per_page_count=per_page_count)

        for item in all_notifications:

                item.is_read=True
                item.save()
        if not is_paginate:
            serializer_data= [
                 {
                    "id":notification_obj.id,
                    "title":notification_obj.title,
                    "jtime":notification_obj.jtime(),
                    "sub_title":notification_obj.sub_title,
                    "custom_data":notif_data(notification_obj=notification_obj,workspace_obj=workspace_obj if notification_obj.workspace else None )
                 } for notification_obj in notification_objs if workspace_obj== notification_obj.workspace or not notification_obj.workspace
            ]
        else:
            data_list =[]
            for notification_obj in notification_objs['list']:
                if workspace_obj == notification_obj.workspace or not notification_obj.workspace:
                    dic ={
                        "id": notification_obj.id,
                        "title": notification_obj.title,
                        "jtime": notification_obj.jtime(),
                        "sub_title": notification_obj.sub_title,
                        "custom_data": notif_data(notification_obj=notification_obj,
                                                  workspace_obj=workspace_obj if notification_obj.workspace else None)
                    }
                    data_list.append(dic)
            notification_objs['list']= data_list
        if not is_paginate:
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data

            })
        else:
            return Response(status=status.HTTP_200_OK, data={
                "status": True,
                "message": "success",
                "data": notification_objs['list'],
                "extra":{
                    "count":notification_objs['count'],
                    "next":notification_objs['next'],
                    "previous":notification_objs['previous'],
                }

            })


