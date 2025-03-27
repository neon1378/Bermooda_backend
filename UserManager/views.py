from django.shortcuts import render
from django.middleware.csrf import get_token
from rest_framework import mixins
from rest_framework import generics
import re

from core.widgets import change_current_workspace_jadoo

from ProjectManager.models import Project, CategoryProject
from CrmCore.models import GroupCrm
from django.views.decorators.csrf import csrf_protect

from ProjectManager.models import ProjectDepartment
from .models import *
from core.permission import IsWorkSpaceUser
from MailManager.models import MailStatus
from core.models import City,State
from django.contrib.auth.hashers import check_password
import secrets
from CrmCore.models import *
from Notification.views import create_notification
import string
from WalletManager.models import Wallet
from core.views import send_sms,send_invite_link
from django.utils.decorators import method_decorator
from Notification.models import Notification
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
import datetime
from django.utils.timezone import datetime, make_aware
from rest_framework_simplejwt.tokens import RefreshToken
from WorkSpaceManager.models import WorkSpace,WorkspaceMember,WorkSpacePermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
import requests
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser, FormParser
import json
from django.contrib.auth.models import User, Group
from core.permission import IsAccess
from WorkSpaceManager.views import create_permission_for_member
from cryptography.fernet import Fernet
import os

from dotenv import load_dotenv
load_dotenv()
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
key = os.getenv("PHONE_KEY")  # Replace this with your actual generated key

cipher_suite = Fernet(key)



def encrypt(data: str) -> str:
   
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt(encrypted_data: str) -> str:
    
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    return decrypted_data.decode()



def make_workspace_query(user_acc):
    response_data = []
    workspace_owners = WorkSpace.objects.filter(owner=user_acc)
    for workspace in workspace_owners:
        dic = {
            "id": workspace.id,
            "title": workspace.title,
            "is_authenticated": workspace.is_authenticated,
            "jadoo_workspace_id": workspace.jadoo_workspace_id,
            "is_active": workspace.is_active,
            "type": "owner",
            "workspace_permissions": [
                {
                    "id": permission.id,
                    "permission_type": permission.permission_type,
                    "is_active": permission.is_active
                } for permission in WorkSpacePermission.objects.filter(workspace=workspace)
            ],
        }
        response_data.append(dic)
    workspace_members = WorkspaceMember.objects.filter(user_account=user_acc)
    for member in workspace_members:
        dic = {
            "id": member.workspace.id,
            "title": member.workspace.title,
            "is_authenticated": member.workspace.is_authenticated,
            "jadoo_workspace_id": member.workspace.jadoo_workspace_id,
            "is_active": member.workspace.is_active,
            "type": "member",
            "workspace_permissions": [
                {
                    "id": permission.id,
                    "permission_type": permission.permission_type,
                    "is_active": permission.is_active
                } for permission in WorkSpacePermission.objects.filter(workspace=member.workspace)
            ],
        }
        permissions = [
            {
                "id": permission.id,
                "permission_name": permission.permission_name,
                "permission_type": permission.permission_type
            } for permission in member.permissions.all()
        ]
        dic['permissions'] = permissions
        dic['is_accepted'] = member.is_accepted
        response_data.append(dic)
    return response_data

@api_view(['GET'])
@permission_classes([AllowAny])
def create_token (request):

    for item in Group.objects.all():
        print(item.id)
        print(item.name)
        for perm in  item.permissions.all():
            print (perm.content_type,"@@@")
    return Response(status=status.HTTP_200_OK,data={"token":"asd"})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token (request):

    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # x_forwarded_for can contain multiple IPs, take the first one
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
      
        x_api_key = request.headers.get("x-api-key")
    
        if x_api_key == JadooToken.objects.last().token:
            
            csrf_token = get_token(request)
            return Response(status=status.HTTP_200_OK,data={"status":True,"data":{"csrf_token":csrf_token,"ip":ip}})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    except:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([AllowAny])
def authuser(request):
   
        data= request.data
        code = data['code']

        username = data['phone_number']
        try:
            user = UserAccount.objects.get(username=username)
            token = Token.objects.get_or_create(user=user)[0]
            if user.is_super_manager:
                if int(code) == 8201:
                    return Response(status=status.HTTP_202_ACCEPTED,data={"status":True,"message":"با موفقیت انجام شد","token":str(token)})
            else:
                if int (user.verify_code) == int(code):
                    
                    return Response(status=status.HTTP_202_ACCEPTED,data={"status":True,"message":"با موفقیت انجام شد","token":str(token)})
            
            return Response(status=status.HTTP_401_UNAUTHORIZED,data={"status":False,"message":"کد تایید اشتاه است"})
                
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED,data={"status":False,"message":"کاربر مورد نظر وجود ندارد"})






@api_view(['GET'])
@permission_classes([AllowAny])

def create_state_and_city(request):
    
    with open('states.json', 'r', errors='ignore', encoding='UTF-8') as file:
            # Load the JSON data
        data = json.load(file)

        for state in data:
            new_state =State(
                name = state['name'],
                code =state['code']
            )
            new_state.save()
            city_list= []
            for city in state['citys']:
                new_city= City(
                    name = city['name'],
                    code = city['code']
                )
                new_city.save()
                city_list.append(new_city)
            new_state.city.set(city_list)
   
    return Response(status=status.HTTP_200_OK,data=data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_state (request):
    states = State.objects.all()
    
    state_list = [{"name": state.name, "id": state.id} for state in states]
    
    return Response (status=status.HTTP_200_OK,data={
        "status":True,
        "message":"succses",
        "data":state_list
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_city_per_state (request,state_id):
    state_obj = State.objects.get(id=state_id)
    city_list = [{
        "name": city.name,
        "id": city.id
    } for city in state_obj.city.all()]
    return Response (status=status.HTTP_200_OK,data={
        "status":True,
        "messag":"succses",
        "data":city_list
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_info(request):
    workspace_obj= get_object_or_404(WorkSpace,id=request.GET.get("workspace_id",None))
    user_acc_list = []
    for workspace_member in WorkspaceMember.objects.filter(workspace=workspace_obj):


            dic = {
                    "fullname":workspace_member.user_account.fullname,
                    "id":workspace_member.user_account.id,
                    "avatar_url":workspace_member.user_account.avatar_url(),
                    "self":workspace_member.user_account == request.user,
                    "type":"member",
                    "permissions":[],
                    "member_id" :workspace_member.id,

            }

            for permission in workspace_member.permissions.all():
                dic['permissions'].append({
                    "permission_name":permission.permission_name,
                    "permission_type":permission.permission_type
                })


            user_acc_list.append(dic)


    user_acc_list.append(
            {
                "fullname":workspace_obj.owner.fullname,
                "id":workspace_obj.owner.id,
                "avatar_url": workspace_obj.owner.avatar_url(),
                "self": request.user == workspace_obj.owner,
                "type":"owner",
                "member_id":"555",
                "permissions":[]

            }
        )
    for item in user_acc_list:
        print(item['member_id'])
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"succses",
        "data":user_acc_list
    })

    





@api_view(['POST'])
@permission_classes([AllowAny])
# @parser_classes([MultiPartParser, FormParser]) 
def test_file (request):
    # print (request.FILES)
    # print(request.data)
    # State.objects.all().delete()
    # City.objects.all().delete()
    url = "https://server.jadoo.app/api/v1/states"
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vc2VydmVyLmphZG9vLmFwcC9hcGkvdjEvdXNlci9hdXRoL2NyZWF0ZUJ1c2luZXNzVXNlciIsImlhdCI6MTczOTM1NDkzNCwiZXhwIjoxNzQwNTY0NTM0LCJuYmYiOjE3MzkzNTQ5MzQsImp0aSI6InliMWp5YWNOWWRBMkxwejMiLCJzdWIiOiI1MiIsInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.5Sbt2iZhax9pvd4bx8-BBgHn7C2UU1PljKhdYq4rpME"
    headers = {
        "contnet-type":"application/json",
        "Authorization" :f"Bearer {token}"
    }
    response = requests.get(url=url,headers=headers)
    
    states = response.json()
    
    for state in states['data'] :
        try :
            state_obj= State.objects.get(name=state['title'])
            state_obj.refrence_id= state['id']
            state_obj.latitude=state['latitude']
            state_obj.longitude=state['longitude']
            state_obj.save()
            url_city = f"https://server.jadoo.app/api/v1/cities/getByStateId/{state['id']}"
            response = requests.get(url=url_city,headers=headers)
            cities = response.json()
            for city1 in cities['data']:
                try:
                    city_exsist = state_obj.city.get(name=city1['title'])
                    city_exsist.refrence_id= city1['id']
                    city_exsist.latitude=city1['latitude']
                    city_exsist.longitude=city1['longitude']
                except:
                    new_city_obj = City.objects.create(
                        refrence_id= city1['id'],
                        name=city1['title'],
                        latitude=city1['latitude'],
                        longitude=city1['longitude']
                    )
                    new_city_obj.save()
                    state_obj.city.add(new_city_obj)
                    
        except:
            new_state_obj = State(
                name=state['title'],
                refrence_id= state['id'],
                latitude=state['latitude'],
                longitude=state['longitude']
            )
            new_state_obj.save()
            url_city = f"https://server.jadoo.app/api/v1/cities/getByStateId/{state['id']}"
            response = requests.get(url=url_city,headers=headers)
            cities = response.json()
            for city1 in cities['data']:
                new_city_obj = City.objects.create(
                        refrence_id= city1['id'],
                        name=city1['title'],
                        latitude=city1['latitude'],
                        longitude=city1['longitude']
                )
                new_city_obj.save()
                new_state_obj.city.add(new_city_obj)
    return Response(status=status.HTTP_200_OK)

class ReadyTextManager(APIView):
    permission_classes=[IsAuthenticated]
    def get (self,request,ready_text_id=None):
        workspace_id= request.GET.get("workspace_id")
        if ready_text_id:
            ready_text_obj = get_object_or_404(ReadyText,id=ready_text_id)
            serializer_data =ReadyTextSerializer(ready_text_obj)
            return Response(status=status.HTTP_200_OK,data={"status":True,"message":"succsec","data":serializer_data.data})

        ready_text_objs = ReadyText.objects.filter(owner=request.user,workspace_id=workspace_id)
        serializer_data =ReadyTextSerializer(ready_text_objs,many=True)
        return Response(status=status.HTTP_200_OK,data={"status":True,"message":"succsec","data":serializer_data.data})

    def post (self,request):
        request.data['owner_id'] = request.user.id
        serializer_data = ReadyTextSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()

            return Response(status=status.HTTP_201_CREATED,data={"status":True,"message":"پیام آماده با موفقیت ثبت شد","data":serializer_data.data})
        
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer_data.errors)
    def put (self,request,ready_text_id):
        ready_text_obj =get_object_or_404(ReadyText,id=ready_text_id)
        serializer = ReadyTextSerializer(ready_text_obj,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={"status":True,"message":"پیام آماده با موفقیت آپدیت شد","data":serializer.data})
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer.errors)
    
    def delete(self,request,ready_text_id):
        ready_text_obj =get_object_or_404(ReadyText,id=ready_text_id)
        ready_text_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






    

#  client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0]
#User Registeration Begin

@api_view(['POST'])
@permission_classes([AllowAny])
def get_phone_number (request):
    data =request.data
    phone_number = data['phone_number']
    request_type = data.get("request_type",None)
    pattern = r"^09\d{9}$"
    if not re.match(pattern, phone_number):
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"شماره تلفن وارد شده اشتباه میباشد"
        })

    try :
        user_acc = UserAccount.objects.get(phone_number=phone_number)

        user_acc.is_staff=False
        user_acc.save()
        if request_type == "change password":
                if UserAccount.objects.filter(phone_number=phone_number).exists():
                    verify_code = random.randint(100000, 999999)
                    send_sms(phone_number=phone_number,verify_code=verify_code)
                    user_acc.verify_code=verify_code
                    user_acc.expire_verify_code=datetime.now().time()
                    user_acc.save()
                    return Response(status=status.HTTP_200_OK,data={
                        "status":True,
                            "message":"کد تایید با موفقیت ارسال شد",
                            "data":{
                                "phone_number":phone_number
                            }

                    })
                return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"کاربر مورد نظر وجود ندارد"
                })
        if user_acc.is_register:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"کاربر از قبل ثبت نام شده است",
                "data":{}
            })
        if not user_acc.is_expired():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "status": False,
                "message": "لطفا چند دقیقه دیگر امتحان کنید"
            })
        else:
            verify_code = random.randint(100000, 999999)
            send_sms(phone_number=phone_number,verify_code=verify_code)
            user_acc.verify_code=verify_code
            user_acc.expire_verify_code=datetime.now().time()
            user_acc.save()
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"کد تایید با موفقیت ارسال شد",
                "data":{
                    "phone_number":phone_number
                }

            })
    
    except:
        verify_code = random.randint(100000, 999999)
        new_user_acc = UserAccount(
            phone_number=phone_number,
            verify_code=verify_code,
            is_staff=False

        )
      
        new_user_acc.expire_verify_code=datetime.now().time()
        new_user_acc.save()
        send_sms(phone_number=phone_number,verify_code=verify_code)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"کد تایید با موفقیت ارسال شد",
            "data":{
                "phone_number":phone_number
            }
        })

    

    




@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone_number  (request):
    data= request.data
    phone_number = data['phone_number']
    code = data['code']
    user_acc = get_object_or_404(UserAccount,phone_number=phone_number)
    if user_acc.is_expired() :
        return Response(status=status.HTTP_401_UNAUTHORIZED,data={
            "status":False,
            "message":"کد تایید اشتباه میباشد"
        })
    if int(user_acc.verify_code) == int(code):
      
 
        refresh = RefreshToken.for_user(user_acc)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"تایید شد",
            "data":{
     
                "access":str(refresh.access_token)
            }
        })
    else: 
        return Response(status=status.HTTP_401_UNAUTHORIZED,data={
            "status":False,
            "message":"کد تایید اشتباه میباشد"
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_user_password(request):
    data= request.data
    password = data['password']
    confirm_password = data['confirm_password']
    if password != confirm_password:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"رمز عبور و تکرار آن مطابقت ندارد",
            "data":{}
        })
    
    refresh = RefreshToken.for_user(request.user)
    request.user.set_password(password)
    request.user.save()
    return Response(status =status.HTTP_202_ACCEPTED,data={
        "status":True,
        "message":"رمز عبور شما با موفقیت تغییر کرد",
        "data":{
                'refresh': str(refresh),
                'access': str(refresh.access_token),

        }
    })

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_username_pass(request):
   

    user_acc =request.user

    data= request.data
    # username=data['username']
    password = data['password']
    avatar_id = data.get("avatar_id",None)
    confirm_password = data['confirm_password']
    fullname = data['fullname']

    if password != confirm_password:
            
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"رمز عبور ها با هم شباهت ندارند",
                "data":{}
            })
    if WorkspaceMember.objects.filter(user_account=user_acc).exists():
        current_workspace=WorkspaceMember.objects.filter(user_account=user_acc).first()
        change_current_workspace_jadoo(user_acc=user_acc, workspace_obj=current_workspace)
        user_acc.current_workspace_id=current_workspace.workspace.id
        user_acc.save()
            
    refresh = RefreshToken.for_user(user_acc)

        

    user_acc.set_password(password)
    user_acc.is_register= True
    user_acc.fullname=fullname
    if avatar_id:
        main_file = MainFile.objects.get(id=avatar_id)
        main_file.its_blong=True
        user_acc.avatar =main_file

    user_acc.save()
    try:
        jadoo_base_url = os.getenv("JADOO_BASE_URL")
            #send user to jadoo

        url = f"{jadoo_base_url}/user/auth/createBusinessUser"
        payload = {
                    "mobile":user_acc.phone_number,

                    "password":password,

                }
        response_data = requests.post(url=url,data=payload)
        print(response_data.json())
        recive_data =response_data.json()

        user_acc.refrence_id= int(recive_data['data']['id'])
        user_acc.refrence_token= recive_data['data']['token']
    except:
        pass



    user_acc.save()
    return Response(status=status.HTTP_201_CREATED,data={
            "status":True,
            "message":"با موفقیت  انجام شد",
            "data":{
                'jwt_token':{
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                "token":str(Token.objects.get_or_create(user=user_acc)[0]),
                "workspaces":make_workspace_query(user_acc=user_acc),
                "jadoo_token":user_acc.refrence_token,
                "refrence_id":user_acc.refrence_id
            }
        })

    




#User Registration End

#User Login Begin 

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    data= request.data
    username = data['username']
    password = data['password']
    try :
        try:
            user_acc = UserAccount.objects.get(username = username)
        except:
            user_acc=UserAccount.objects.get(phone_number=username)
        if check_password(password,user_acc.password):
            token = Token.objects.get_or_create(user=user_acc)
            refresh = RefreshToken.for_user(user_acc)
            refresh_expiry = datetime.fromtimestamp(refresh.access_token.payload['exp'])
            refresh_expiry_aware = make_aware(refresh_expiry)
            jadoo_server =os.getenv("JADOO_BASE_URL")
            try:
                url = f"{jadoo_server}/user/auth/getUserTokenById?id={user_acc.refrence_id}"
                response = requests.get(url=url)
                print(response.json())
                respnse_data = response.json()
                user_acc.refrence_token=respnse_data['data']['token']
                user_acc.save()
            except:
                pass
            workspaces = WorkSpace.objects.filter(owner=user_acc).first()
            if user_acc.current_workspace_id == 0 or  not WorkSpace.objects.filter(id=user_acc.current_workspace_id).exists():
                if workspaces:
                    change_current_workspace_jadoo(user_acc=user_acc,workspace_obj=workspaces)
                    user_acc.current_workspace_id = workspaces.id
                    user_acc.save()
            workspace_member = WorkspaceMember.objects.filter(user_account=user_acc)

            for member in workspace_member:
                if user_acc.current_workspace_id == 0 or not WorkSpace.objects.filter(id=user_acc.current_workspace_id).exists():
                    if member.is_accepted:
                        change_current_workspace_jadoo(user_acc=user_acc, workspace_obj=member.workspaces)
                        user_acc.current_workspace_id=member.workspace.id

                        user_acc.save()
                        break





            

            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":{
                    'jwt_token':{
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'refresh_expires_at': refresh_expiry_aware.isoformat(),
                    },
                    "token":str(token[0]),
                    "jadoo_token":user_acc.refrence_token,
                    "workspaces":make_workspace_query(user_acc=user_acc),
                    "refrence_id":user_acc.refrence_id
                }
            })
        return Response(status=status.HTTP_401_UNAUTHORIZED,data={
            "status":False,
            "message":"نام کاربری یا رمز عبور اشتباه میباشد",
            "data":{}
        })
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED,data={
            "status":False,
            "message":"نام کاربری یا رمز عبور اشتباه میباشد",
            "data":{}
        })

#User Login End 


class UserAccountManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceUser]
    def get (self,request,user_id=None):
        workspace_id = request.GET.get("workspace_id")
        response_data = []
        workspae_obj = get_object_or_404(WorkSpace, id=workspace_id)
        base_url = os.getenv("BASE_URL")
        if user_id:
            user_obj =get_object_or_404(UserAccount,id=user_id)
            workspace_member = WorkspaceMember.objects.get(user_account=user_obj,workspace=workspae_obj)
            serializers_data =UserAccountSerializerShow(user_obj).data
            if user_obj != workspae_obj.owner:
                serializers_data['jtime'] = workspace_member.jtime()
                serializers_data['member_id'] = workspace_member.id
                serializers_data['fullname'] = workspace_member.fullname
                serializers_data['is_accepted'] = workspace_member.user_account.is_register
                serializers_data['type'] = "member"
                try:
                    serializers_data['avatar_url'] = {
                        "id": workspace_member.avatar.id,
                        "url": f"{base_url}{workspace_member.avatar.file.url}"
                    }
                except:
                    serializers_data['avatar_url'] = {}
            else:

                serializers_data['avatar_url'] = {
                        "id": user_obj.avatar.id,
                        "url": f"{base_url}{user_obj.avatar.file.url}"
                    } if user_obj.avatar else {}
                serializers_data['fullname'] = user_obj.fullname

                serializers_data['type'] = "owner"

            return Response(status=status.HTTP_200_OK,data={
                    "status":True,
                    "message":"موفق",
                    "data":serializers_data
                })

        if workspae_obj.owner != request.user:
            owner_serializer = UserAccountSerializerShow(workspae_obj.owner).data
            owner_serializer['jtime'] = workspae_obj.owner.jtime()
            owner_serializer['member_id'] = workspae_obj.owner.id
            owner_serializer['fullname'] = workspae_obj.owner.fullname
            owner_serializer['is_accepted'] = workspae_obj.owner.is_register
            owner_serializer['type'] ="owner"
            try:
                owner_serializer['avatar_url'] = {
                    "id": owner_serializer.avatar.id,
                    "url": f"{base_url}{workspae_obj.owner.avatar.file.url}"
                }
            except:
                owner_serializer['avatar_url'] = {}
            response_data.append(owner_serializer)

        for workspace_member in WorkspaceMember.objects.filter(workspace=workspae_obj):

            
            serializers_data =UserAccountSerializerShow(workspace_member.user_account).data
            serializers_data['jtime'] = workspace_member.jtime()
            serializers_data['member_id'] = workspace_member.id
            serializers_data['fullname'] = workspace_member.fullname
            serializers_data['is_accepted'] = workspace_member.user_account.is_register
            serializers_data['type'] = "member"
            try:
                serializers_data['avatar_url'] = {
                    "id": workspace_member.avatar.id,
                    "url": f"{base_url}{workspace_member.avatar.file.url}"
                }
            except:
                serializers_data['avatar_url'] = {}
            response_data.append(serializers_data)
        return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":response_data
            })
    def post(self,request):
        data =request.data
        base_url = os.getenv("BASE_URL")
        workspace_obj =get_object_or_404(WorkSpace,id=data['workspace_id'])
   
        phone_number = data['phone_number']
        permissions = data.get("permissions",[])
        avatar_id = data.get("avatar_id",None)

        try :
            user_acc = UserAccount.objects.get(phone_number=phone_number)
            if WorkspaceMember.objects.filter(workspace=workspace_obj,user_account=user_acc).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"کاربر مورد نظر درحال حاضر در میز کار شما وجود دارد"
                })
            user_acc.phone_number=data['phone_number']
            new_workspace_member = WorkspaceMember(is_accepted=True,workspace=workspace_obj,user_account=user_acc,fullname=f"{data['first_name']} {data['last_name']}")
            if avatar_id:
                main_file =MainFile.objects.get(id=avatar_id)
                main_file.its_blong =True
                main_file.save()

                new_workspace_member.avatar =main_file

            new_workspace_member.save()
            response_data =UserAccountSerializerShow(user_acc)
            response_data.data['fullname']= new_workspace_member.fullname
            response_data.data['jtime'] = new_workspace_member.jtime()
            response_data.data['member_id'] = new_workspace_member.id

            try:
                response_data.data['avatar_url'] = {
                    "id":new_workspace_member.avatar.id,
                    "url": f"{base_url}{new_workspace_member.avatar.file.url}"
                }
            except:
                response_data.data['avatar_url'] ={}
            workspace_owner = workspace_obj.owner.fullname

            send_invite_link(user_acc.phone_number,workspace_owner,workspace_obj.title)
            create_permission_for_member(member_id=new_workspace_member.id)
            sub_title =f"شما به میز کار {workspace_obj.title} توسط {workspace_obj.owner.fullname} دوعوت شده اید"
            title = "دعوت به میزکار"
            # create_notification(related_instance=new_workspace_member,workspace=None,user=new_workspace_member.user_account,title=title,sub_title=sub_title,side_type="invitation")

            return Response(status=status.HTTP_201_CREATED,data={
                    "status":True,   
                    "message":"موفق",
                    "data":response_data.data
                })
        except:
            main_data = {
                "fullname":f"{data['first_name']} {data['last_name']}",
                "phone_number":data['phone_number'] 
                
            }
            serializers_data = UserAccountSerializer(data = main_data)
            if serializers_data.is_valid():
        
                new_user_acc = serializers_data.save()

                new_user_acc.current_workspace_id = workspace_obj.id
                new_user_acc.save()
                new_workspace_member= WorkspaceMember(is_accepted=True,workspace=workspace_obj,user_account=new_user_acc,fullname=main_data['fullname'])
                if avatar_id:
                    main_file = MainFile.objects.get(id=avatar_id)
                    main_file.its_blong = True
                    main_file.save()

                    new_workspace_member.avatar = main_file
                new_workspace_member.save()

                create_permission_for_member(member_id=new_workspace_member.id,permissions=permissions)
                response_data =UserAccountSerializerShow(new_user_acc)
                response_data.data['fullname']= new_workspace_member.fullname
                response_data.data['jtime'] = new_workspace_member.jtime()
                response_data.data['member_id'] = new_workspace_member.id
                response_data.data['fullname'] = new_workspace_member.user_account.fullname
                try:
                    response_data.data['avatar_url'] = {
                        "id": new_workspace_member.avatar.id,
                        "url": f"{base_url}{new_workspace_member.avatar.file.url}"
                    }
                except:
                    response_data.data['avatar_url'] = {}

                workspace_owner = workspace_obj.owner.fullname
                send_invite_link(new_user_acc.phone_number,workspace_owner,workspace_obj.title)
                sub_title =f"شما به میز کار {workspace_obj.title} توسط {workspace_obj.owner.fullname} دوعوت شده اید"
                title = "دعوت به میزکار"
                # create_notification(related_instance=new_workspace_member,workspace=None,user=new_workspace_member.user_account,title=title,sub_title=sub_title,side_type="invitation")
                return Response(status=status.HTTP_201_CREATED,data={
                    "status":True,
                    "message":"موفق",
                    "data":response_data.data
                })
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "data":serializers_data.errors
            }) 
        
    def put(self, request):
            data = request.data
            user = request.user
            personal_type = data.get("personal_type")

            # Shared fields
            shared_fields = {
                "national_code": data.get("national_code"),
                "email": data.get("email"),
                "phone_number": data.get("phone_number"),
            }

            # Update for "حقیقی" (Natural Person)

            if personal_type == "حقیقی":
                user.fullname = data.get("fullname")
                for field, value in shared_fields.items():
                    setattr(user, field, value)

                user.save()
                return Response(
                    status=status.HTTP_202_ACCEPTED,
                    data={
                        "status": True,
                        "message": "با موفقیت آپدیت شد",
                        "data": {
                            "id": user.id,
                            "fullname": user.fullname,
                            "national_code": user.national_code,
                            "email": user.email,
                            "phone_number": user.phone_number,
                        },
                    },
                )

            # Update for "حقوقی" (Legal Person)
            elif personal_type == "حقوقی":
                user.brand_name = data.get("brand_name")
                user.economic_code = data.get("economic_code")
                for field, value in shared_fields.items():
                    setattr(user, field, value)

                user.save()
                return Response(
                    status=status.HTTP_202_ACCEPTED,
                    data={
                        "status": True,
                        "message": "با موفقیت آپدیت شد",
                        "data": {
                            "id": user.id,
                            "brand_name": user.brand_name,
                            "national_code": user.national_code,
                            "economic_code": user.economic_code,
                            "email": user.email,
                            "phone_number": user.phone_number,
                        },
                    },
                )

            # Invalid personal_type
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "status": False,
                    "message": "personal_type is not correct",
                    "data": {},
                },
            )
    def delete (self,request,user_id):
        
        user_account = get_object_or_404(UserAccount,id=user_id)
        workspace_obj = get_object_or_404(WorkSpace,id=request.data['workspace_id'])
        members = WorkspaceMember.objects.filter(workspace=workspace_obj,user_account=user_account)
        members.delete()
   
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workspaces (request):
    response_data = []
    workspace_owners = WorkSpace.objects.filter(owner= request.user)
    for workspace in workspace_owners:
        dic = {
            "id":workspace.id,
            "title":workspace.title,
            "is_authenticated":workspace.is_authenticated,
            "jadoo_workspace_id":workspace.jadoo_workspace_id,
            "is_active":workspace.is_active,
            "type":"owner",
            "workspace_permissions":[
                {
                    "id":permission.id,
                    "permission_type":permission.permission_type,
                    "is_active":permission.is_active
                } for permission in WorkSpacePermission.objects.filter(workspace=workspace)
            ],
        }
        response_data.append(dic)
    workspace_members = WorkspaceMember.objects.filter(user_account=request.user)
    for member in workspace_members:
        dic ={
            "id": member.workspace.id,
            "title": member.workspace.title,
            "is_authenticated": member.workspace.is_authenticated,
            "jadoo_workspace_id": member.workspace.jadoo_workspace_id,
            "is_active": member.workspace.is_active,
            "type": "member",
            "workspace_permissions": [
                {
                    "id": permission.id,
                    "permission_type": permission.permission_type,
                    "is_active": permission.is_active
                } for permission in WorkSpacePermission.objects.filter(workspace=member.workspace)
            ],
        }
        permissions = [
            {
                "id": permission.id,
                "permission_name": permission.permission_name,
                "permission_type": permission.permission_type
            } for permission in member.permissions.all()
        ]
        dic['permissions'] = permissions
        dic['is_accepted'] = member.is_accepted
        response_data.append(dic)



    return Response(status=status.HTTP_200_OK,data= {
        "status":True,
        "message":"موفق",
        "data":response_data
    })





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_workspace(request):

    if WorkSpace.objects.filter(owner=request.user).count() == 10:
        return  Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"شما نمیتوانید بیشتر از ۱۰ کسب کار داشته باشید"
        })
    data= request.data

    new_workspace_obj = WorkSpace(title= data['title'])
    new_workspace_obj.owner=request.user
    new_workspace_obj.save()
    permission_list = [
        "project_board",
        "crm",
        "marketing_status",
        "group_chat",
        "letters",
        "planing",
    ]
    for permission in permission_list:
        WorkSpacePermission.objects.create(
            permission_type= permission,
            workspace = new_workspace_obj,

        )

    if BonosPhone.objects.filter(phone=request.user.phone_number).count() <3:
        if BonosPhone.objects.filter(phone=request.user.phone_number).count() ==1 :
            new_workspace_obj.is_team_bonos=True
            new_workspace_obj.save()
        BonosPhone.objects.create(phone=request.user.phone_number)

        new_wallet = Wallet(workspace=new_workspace_obj,balance=50000)
    else:

        new_wallet = Wallet(workspace=new_workspace_obj,balance=0)

    new_wallet.save()
    request.user.current_workspace_id = new_workspace_obj.id
    request.user.save()

    default_statuses = [
            {
                "title":"امضا شده",
                
            },
            {
                "title":"در انتظار امضا",
                
                
            },
            {
                "title":"معلق",
                
            },

            {
                "title":"منتظر پاسخ",
                
            },
            {
                "title":"بایگانی شده",
                
            },
            {
                "title":"پیش نویس",
            },

        ]
    
    for statuss in default_statuses:
        mail_status_obj = MailStatus.objects.create(title=statuss['title'],workspace=new_workspace_obj)
                
    new_project_department = ProjectDepartment.objects.create(title="بورد پروژه",workspace=new_workspace_obj,manager=request.user)
    new_project= Project.objects.create(
        title="پیشفرض",
        workspace = new_workspace_obj,

        department = new_project_department
    )
    categories = [
        {"title": "برای انجام", "order": 1, "color_code": "#DB4646"},
        {"title": "در حال انجام", "order": 2, "color_code": "#02C875"},
        {"title": "انجام شده", "order": 3, "color_code": "#9C00E8"},
        {"title": "تست", "order": 4, "color_code": "#E82BA3"},
    ]
    category_objs = [
        CategoryProject.objects.create(
            title=category['title'],
            color_code=category['color_code'],
            order=category['order'],
            project=new_project
        ) for category in categories
    ]
    new_project.members.add(request.user)
    new_project.save()
    new_crm_department = CrmDepartment.objects.create(title="بورد مشتری",workspace=new_workspace_obj,manager=request.user)
    new_group_crm = GroupCrm.objects.create(
        title="پیشفرض",
        workspace = new_workspace_obj,

        department = new_crm_department
    )
    label_list = [
        {
            "title": "کشف مشتری ",
            "color_code": "#E82BA3",
            "order": 1,
            "steps": [
                {
                    "title": "جذب",
                    "step": 1,
                },
                {
                    "title": "جمع‌آوری اطلاعات",
                    "step": 2,
                },
                {
                    "title": "تماس اولیه ",
                    "step": 3,
                },

                {
                    "title": "تکمیل اطلاعات ",
                    "step": 4,
                },
                {
                    "title": "تعیین وضعیت",
                    "step": 5,
                },
            ]

        },
        {
            "title": "معرفی محصول/ خدمات",
            "color_code": "#DB4646",
            "order": 2,
            "steps": [
                {
                    "title": "نیازسنجی",
                    "step": 1,
                },
                {
                    "title": "پیشنهاد اولیه",
                    "step": 2,
                },
                {
                    "title": "ارائه محصول / خدمات",
                    "step": 3,
                },

                {
                    "title": "  نیاز ها و ابهامات ",
                    "step": 4,
                },
                {
                    "title": "بازخورد",
                    "step": 5,
                },
            ]
        },

        {
            "title": "پیشنهاد / ارزیابی",
            "color_code": "#02C875",
            "order": 3,
            "steps": [
                {
                    "title": "تهیه پیشنهاد",
                    "step": 1,
                },
                {
                    "title": "مذاکره و سفارشی‌سازی ",
                    "step": 2,
                },
                {
                    "title": "آزمایش یا تست محصول",
                    "step": 3,
                },

                {
                    "title": "پیگیری مشتری",
                    "step": 4,
                },
            ]
        },

        {
            "title": "فاکتور / قرارداد",
            "color_code": "#04C4B7",
            "order": 4,
            "steps": [
                {
                    "title": "تهیه پیش‌ فاکتور/قرارداد   ",
                    "step": 1,
                },
                {
                    "title": "نهایی‌سازی فاکتور/قرارداد ",
                    "step": 2,
                },
                {
                    "title": "تایید پرداخت اولیه   ",
                    "step": 3,
                },

                {
                    "title": "هماهنگی برای تحویل    ",
                    "step": 4,
                },
                {
                    "title": "ثبت و بایگانی مدارک ",
                    "step": 5,
                },
            ]
        },

        {
            "title": "بسته شده",
            "color_code": "#636D74",
            "order": 5,
            "steps": [
                {
                    "title": "تحویل محصول یا ارائه خدمت ",
                    "step": 1,
                },
                {
                    "title": "آموزش و مشاوه  ",
                    "step": 2,
                },

                {
                    "title": "پشتیبانی فروش ",
                    "step": 3,
                },
                {
                    "title": "نعیین وضعیت فروش مجدد ",
                    "step": 4,
                },
            ]
        },
    ]

    for label in label_list:
        new_label_obj = Label(order=label['order'], title=label['title'], color=label['color_code'],
                              group_crm=new_group_crm)
        new_label_obj.save()
        new_label_step = LabelStep.objects.create(label=new_label_obj)
        for step in label['steps']:
            new_step = Step.objects.create(
                title=step['title'],
                step=step['step'],
                label_step=new_label_step
            )

    new_group_crm.members.add(request.user)
    new_group_crm.save()

    return Response(status=status.HTTP_201_CREATED,data={
        "status":True,
        "message":"succsec",
        "data":{
            ""
            "title":new_workspace_obj.title,
            "id":new_workspace_obj.id,
            "is_team_bonos":new_workspace_obj.is_team_bonos,
            "workspace_bonos":BonosPhone.objects.filter(phone=request.user.phone_number).count() < 3

        }
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data (request):
    data=request.data

    user_data = {
        "id":request.user.id,
        "fullname":request.user.fullname,
        # "last_name":request.user.last_name,
        "username":request.user.username,
        "personal_type":request.user.personal_type,
        "phone_number":request.user.phone_number,
        "city_name":request.user.city_name(),
        "state_name":request.user.state_name(),
        "is_profile":request.user.is_profile,
        "email":request.user.email,
        "avatar_url":request.user.avatar_url(),
        "is_auth":request.user.is_auth,
        "jtime":request.user.jtime()
       
       
    }

    try :
        current_workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        dic = {
            "wallet":{
                "id":current_workspace_obj.wallet.id,
                "balance":current_workspace_obj.wallet.balance
            },
            "id":current_workspace_obj.id,
            "title":current_workspace_obj.title,
            "is_authenticated":current_workspace_obj.is_authenticated,
            "jadoo_workspace_id":current_workspace_obj.jadoo_workspace_id,
            "is_active":current_workspace_obj.is_active,
            "workspace_permissions":[
                {
                    "id":permission.id,
                    "permission_type":permission.permission_type,
                    "is_active":permission.is_active
                } for permission in WorkSpacePermission.objects.filter(workspace=current_workspace_obj)
            ],
            "unread_notifications":Notification.objects.filter(workspace=current_workspace_obj,user_account=request.user,is_read=False).count() + Notification.objects.filter(user_account=request.user,is_read=False).count() 

        }
        if request.user == current_workspace_obj.owner:
            dic['type'] = "owner"
        else:
            try:
                workspac_member = WorkspaceMember.objects.get(workspace=current_workspace_obj,user_account=request.user)
                permissions = [
                        {
                            "id":permission.id,
                            "permission_name":permission.permission_name,
                            "permission_type":permission.permission_type
                        } for permission in workspac_member.permissions.all()
                    ]
                dic['permissions']=permissions
                dic['is_accepted']=workspac_member.is_accepted
            except:
                pass
            dic['type'] = "member"
        user_data['current_workspace'] = dic
    except:
        user_data['current_workspace'] = None
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"succses",
        "data":user_data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_current_worksapce (request):
    data = request.data
    workspace_obj = get_object_or_404(WorkSpace,id=data.get("workspace_id"))
    change_current_workspace_jadoo(user_acc=request.user,workspace_obj=workspace_obj)
    request.user.current_workspace_id= data.get("workspace_id")

    request.user.save()
    return Response(status=status.HTTP_202_ACCEPTED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_username(request):
    data= request.data

    fullname = data['fullname']

    avatar_id = data.get("avatar_id",None)




    request.user.fullname = fullname
    if avatar_id:
        if request.user.avatar:
            if avatar_id != request.user.avatar.id:
                request.user.avatar.delete()
                main_file = MainFile.objects.get(id=avatar_id)
                main_file.its_blong=True
                main_file.save()
                request.user.avatar = main_file
        else:
            main_file = MainFile.objects.get(id=avatar_id)
            main_file.its_blong = True
            main_file.save()
            request.user.avatar = main_file
    request.user.save()
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":{}
    })



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_user_profile_password(request):
    data =request.data
    current_password = data.get("current_password")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if current_password:
        if check_password(current_password,request.user.password):
            if password == confirm_password:

                request.user.set_password(password)
                request.user.save()
                return Response(status=status.HTTP_202_ACCEPTED,data={
                    "status":True,
                    "message":"با موفقیت آپدیت شد",
                    "data":{}
                })
            
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"رمز عبور ها باهم شباهت ندارند",
                    "data":{}
                })

        return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"رمز عبور فعلی اشتباه میباشد ",
                    "data":{}
                })

    return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":True,
                    "message":"",
                    "data":{}
                })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_fcm_token(request):
    token = request.data.get('token')
    is_application = request.data.get("is_application",False)

    if not token:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"Token is required",
                    "data":{}
                })
    exsit_fcm = FcmToken.objects.filter(token=token, user_account=request.user)
    if exsit_fcm.exists():
        if len(exsit_fcm) >1:
            for fcm in exsit_fcm:
                fcm.delete()
        

    fcm_token, created = FcmToken.objects.get_or_create(
            is_application=is_application,
            token=token,
            defaults={'user_account': request.user}
        ) 
    if not created:
            # Update device name and user if necessary
        if fcm_token.user_account != request.user:
            fcm_token.user_account = request.user
            
        fcm_token.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def add_user_avatar(request):
    file = request.FILES.get("file")
    new_main_file = MainFile(file=file)
    new_main_file.its_blong=True
    new_main_file.save()
    request.user.avatar.delete()
    request.user.avatar = new_main_file
    request.user.save()
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"با موفقیت بارگزاری شد",
        "data":{}
    })


@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@api_view(['POST']) 
def create_avatar (request):
    
    file = request.FILES.get("file")
    main_file = MainFile(file=file,its_blong = True)
    main_file.save()
    request.user.avatar = main_file 
    request.user.save()
    
    return Response(status=status.HTTP_201_CREATED,data={
        "status":True,
        "message":"success",
        "data":{
            "avtar_url":request.user.avatar_url()
        }
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def account_verify (request):
    user_acc= request.user
    verify_code = random.randint(100000, 999999)
    send_sms(phone_number=user_acc.phone_number,verify_code=verify_code)
    user_acc.verify_code=verify_code
    user_acc.expire_verify_code=datetime.now().time()
    user_acc.save()
    return Response(status=status.HTTP_200_OK)

# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_account (request):
#     data =request.data
#
#     if int(data['code']) == int(request.user.verify_code):
#         request.user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     return Response(status=status.HTTP_400_BAD_REQUEST,data={
#         "status":False,
#         "message":"کد وارد شده اشتباه میباشد",
#         "data":{}
#
#     })
@api_view(["GET"])
@permission_classes([AllowAny])
def change_user(request):
    for user in UserAccount.objects.all():
        user.is_staff= False
        user.save()
    return Response(status=status.HTTP_200_OK)