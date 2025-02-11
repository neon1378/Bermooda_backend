from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from .models import *
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
@api_view(['POST'])
@permission_classes([AllowAny])
def get_fcm_token (request):
    print(request.data)
    return Response(status=status.HTTP_200_OK)
# Create your views here.
def test_chat_ws(request):
    user_id = request.user.id
    return render(request,"SupportManager/firebase.html",context={"user_id":user_id})



@api_view(['GET'])
@permission_classes([AllowAny])
def read_categories(request,workspace_id):
    data = request.data
    workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
    departments = Department.objects.filter(workspace=workspace_obj)
    
    phone_number = data['phone_number']
    fullname=data.get("fullname",None)
    try:
        anon_customer= AnonCustomer.objects.get(phone_number=phone_number)
        room_list =[]
        for department in departments:
            department_not_exist= True
            for room in  Room.objects.filter(workspace= workspace_obj):
                if room.anon_customer == anon_customer and room.department == department:
                    department_not_exist= False
                    dic = {
                        "room_id":room.id,
                        "department":{
                            "id":department.id,
                            "title":department.title,
                            "color_code":department.color_code
                        },
                        
                    }

                    room_list.append(dic)
            if department_not_exist:
                new_room = Room(
                    workspace=workspace_obj,
                    department=department,
                    anon_customer=anon_customer

                )
                new_room.save()
                dic = {
                        "room_id":new_room.id,
                        "department":{
                            "id":department.id,
                            "title":department.title,
                            "color_code":department.color_code
                        },
                        
                    }
                room_list.append(dic)

        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":room_list
        })
    except:
        # pass
        new_anon_customer= AnonCustomer(
            fullname = fullname,
            phone_number=phone_number
        )
        new_anon_customer.save()
        room_list=[]
        for department in departments:
            new_room = Room(
                    workspace=workspace_obj,
                    department=department,
                    anon_customer=new_anon_customer

                )
            new_room.save()
            dic = {
                    "room_id":new_room.id,
                    "department":{
                        "id":department.id,
                        "title":department.title,
                        "color_code":department.color_code
                    },
                        
                }
            room_list.append(dic)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":room_list
        })