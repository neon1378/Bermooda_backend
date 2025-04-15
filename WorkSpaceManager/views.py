from django.db.models.sql import Query
from django.shortcuts import render
from rest_framework import status
from ProjectManager.models import CheckList
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes

from core.widgets import change_current_workspace_jadoo
from .models import *
from rest_framework.decorators import parser_classes
from django.shortcuts import get_object_or_404
import os 
import json
from Notification.models import Notification
from .serializers import WorkSpaceSerializer, IndustrialActivitySerializer, WorkSpaceMemberSerializer, UserSerializer, \
    UpdateWorkSpaceSerializer, WorkSpacePermissionSerializer
import requests
from dotenv import load_dotenv
from core.permission import IsAccess,IsWorkSpaceUser
load_dotenv()
from WalletManager.models import Wallet
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_industrial_activity(request):
    industrial_activity =IndustrialActivity.objects.all()
    serializer_data = IndustrialActivitySerializer(industrial_activity,many=True)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":serializer_data.data

    })

class WorkspaceManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceUser]
    jadoo_base_url = os.getenv("JADOO_BASE_URL")

    def delete(self,request,workspace_id):
        workspace_obj =get_object_or_404(WorkSpace,id=workspace_id)
        if workspace_obj.owner == request.user:
            if request.user.current_workspace_id == workspace_obj.id:
                workspace_member= WorkspaceMember.objects.filter(user_account =request.user).first()
                workspace_owner = WorkSpace.objects.filter(owner= request.user).first()
                if workspace_owner:
                    request.user.current_workspace_id=workspace_owner.id
                elif workspace_member:
                    change_current_workspace_jadoo(user_acc=request.user,workspace_obj=workspace_member.workspace)

                request.user.current_workspace_id = workspace_member.workspace.id
                request.user.save()
            try:
                url = f"{self.jadoo_base_url}/workspace/destroy/{workspace_obj.jadoo_workspace_id}"
                headers = {
                        "content-type": "application/json",
                        "Authorization": f"Bearer {request.user.refrence_token}"
                }

                response= requests.delete(url=url, headers=headers)
                print(response,"!!!!!!!!!!@@@@@")
            except:
                pass



            workspace_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return  Response(status=status.HTTP_403_FORBIDDEN,data={
            "message":"you dont have permission dont try !!!!!!"
        })


    def get(self,request,workspace_id=None):
        if workspace_id:
            workspace_obj= get_object_or_404(WorkSpace,id=workspace_id)
            if workspace_obj.owner == request.user:

                serializer_data =WorkSpaceSerializer(workspace_obj).data

                serializer_data['title'] = workspace_obj.title
                serializer_data['is_authenticated'] = workspace_obj.is_authenticated
                serializer_data['avatar_url']=workspace_obj.avatar_url()
                return Response(status=status.HTTP_200_OK,data=serializer_data)
            

            else:
                return Response(status=status.HTTP_403_FORBIDDEN,data={
                    "status":False,
                    "message":"Access Denied",
                    
                })
        workspace_objs = WorkSpace.objects.filter(owner=request.user)

        serializer_data =WorkSpaceSerializer(workspace_objs,many=True).data
        for data in serializer_data:
            workspace_obj = WorkSpace.objects.get(id=data['id'])
            data['title'] = workspace_obj.title
            data['is_authenticated'] = workspace_obj.is_authenticated
            data['avatar_url']=workspace_obj.avatar_url()



        return Response(status=status.HTTP_200_OK,data=serializer_data)
    def put(self,request,workspace_id):
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        if workspace_obj.owner == request.user:
            data=request.data

            avatar_id = data.get("avatar_id",None)

            serializer_data =WorkSpaceSerializer(workspace_obj,data=request.data)
            if serializer_data.is_valid():
                serializer_data.save()



                if avatar_id:
                    avatar_obj = MainFile.objects.get(id=avatar_id)
                    avatar_obj.its_blong=True
                    avatar_obj.save()
                    workspace_obj.avatar=avatar_obj
                    workspace_obj.save()
                workspace_obj.save()
                try:
                    Wallet.objects.get(workspace=workspace_obj)
                except:
                    new_wallet = Wallet(balance=50000,workspace=workspace_obj)
                    new_wallet.save()

                if workspace_obj.is_authenticated == False:
                    try:
                        url = f"{self.jadoo_base_url}/workspace/store"
                        headers = {
                                    "content-type":"application/json",
                                    "Authorization":f"Bearer {request.user.refrence_token}"
                        }
                        base_url = os.getenv("BASE_URL")



                        payload = {

                                    "cityId":None,
                                    "stateId":None,
                                    "name":workspace_obj.title,
                                    "username":workspace_obj.jadoo_brand_name,
                                    "workspaceId":workspace_obj.id,
                                    "bio":workspace_obj.business_detail,
                                    "avatar":"",
                                    "industrialActivityId":None

                        }


                        if workspace_obj.city:
                            payload['cityId']=workspace_obj.city.refrence_id

                        if workspace_obj.industrialactivity:
                            payload['industrialActivityId']= workspace_obj.industrialactivity.refrence_id


                        if workspace_obj.state:
                            payload['stateId']= workspace_obj.state.refrence_id



                        if workspace_obj.avatar:
                            payload['avatar'] = f"{base_url}{workspace_obj.avatar.file.url}"

                        response = requests.post(url=url,json=payload,headers=headers)

                        response_data_main = response.json()['data']
                        workspace_obj.jadoo_workspace_id= response_data_main['id']
                    except:
                        pass

                workspace_obj.is_authenticated = True
                workspace_obj.save()
                change_current_workspace_jadoo(user_acc=request.user, workspace_obj=workspace_obj)
                # print(response.json())
                print(serializer_data.data)
                serializer_data.data['avatar_url'] = workspace_obj.avatar_url()
                if workspace_obj.wallet.balance <= 0 :
                    workspace_obj.is_active =False
                    workspace_obj.save()
                return Response(status=status.HTTP_202_ACCEPTED,data={
                     "status":True,
                     "message":"success",
                     "data":serializer_data.data
                })
            return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer_data.errors)

        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"Access Denied "
        })



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_workspace_information(request,workspace_id):
    workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
    request.data['user_id'] = request.user.id
    if not request.user == workspace_obj.owner:
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"Access Denied "
        })

    serializer_data = UpdateWorkSpaceSerializer(data=request.data,instance=workspace_obj)
    if serializer_data.is_valid():
        serializer_data.save()
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"با موفقیت به روز رسانی شد",
            "data":serializer_data.data

        })
    return Response(status=status.HTTP_400_BAD_REQUEST, data={
        "status": False,
        "message": "error",
        "data": serializer_data.errors

    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_workspace_personal_information(request,workspace_id):
    workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
    data= request.data
    personal_type = data.get("personal_type")
    fullname = data.get("fullname",None)
    national_code = data.get("national_code",None)
    brand_name = data.get("brand_name",None)
    economic_code = data.get("economic_code",None)
    phone_number = data.get("phone_number",None)
    email = data.get("email",None)
    if personal_type == "حقیقی":
        request.user.fullname=fullname
        request.user.national_code = national_code
        request.user.email=email
        request.user.phone_number = phone_number
        request.user.is_auth=True
        request.user.save()
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"success",
            "data":{
                "id":request.user.id,
                "fullname":request.user.fullname,
                "national_code":request.user.national_code,
                "email":request.user.email,
                "phone_number":request.user.phone_number,
                "is_auth":request.user.is_auth,
               
            }
        })
    elif personal_type == "حقوقی":

        request.user.national_code = national_code
        request.user.email=email
        request.user.phone_number = phone_number
        request.user.brand_name = brand_name
        request.user.economic_code = economic_code

        request.user.is_auth=True
        request.user.save()
                

        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"success",
            "data":{
                "id":request.user.id,
                "brand_name":request.user.brand_name,
                "national_code":request.user.national_code,
                "economic_code":request.user.economic_code,
                "email":request.user.email,
                "phone_number":request.user.phone_number,
                "is_auth":request.user.is_auth
            }
        })
    return Response(status=status.HTTP_400_BAD_REQUEST,data={
        "status":False,
        "message":"personal_type its not correct",
        "data":{}
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def create_category (request):
    jadoo_base_url = os.getenv("JADOO_BASE_URL")
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vc2VydmVyLmphZG9vLmFwcC9hcGkvdjEvdXNlci9hdXRoL2NyZWF0ZUJ1c2luZXNzVXNlciIsImlhdCI6MTczOTcxNDQ4MywiZXhwIjoxNzQwOTI0MDgzLCJuYmYiOjE3Mzk3MTQ0ODMsImp0aSI6Ik1uS1ZUbXBZMGFXVDkyVEgiLCJzdWIiOiI2NSIsInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.oKNvh7AZ2jxIclWGdIk3qbDXoF88pz87NWv6yGoi0oU"
    main_cat__url = f"{jadoo_base_url}/industrialActivity/getIndustrialActivity"
    headers = {
                "Authorization":f"Bearer {token}" 
        }
    response =requests.get(url=main_cat__url,headers=headers)
    for item in response.json()['data']:
        try:
            industrialactivity = IndustrialActivity.objctes.get(refrence_id=item['id'])
            industrialactivity.title = item['title']
            industrialactivity.save()
        except:

            new_industrialactivity= IndustrialActivity.objects.create(
                title = item['title'],
                refrence_id = item['id']
            )

    return Response(status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@api_view(['POST']) 
def create_workspace_image (request,workspace_id):
    workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)

    file = request.FILES.get("file")
    main_file = MainFile(file=file,its_blong = True)
    main_file.save()
    workspace_obj.avatar = main_file 
    workspace_obj.save()
    
    return Response(status=status.HTTP_201_CREATED,data={
        "status":True,
        "message":"success",
        "data":{
            "avatar":workspace_obj.avatar_url()
        }
    })
@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAccess])
def delete_workspace_member(request,member_id):
    workspace_obj = get_object_or_404(WorkSpace,id=request.data['workspace_id'])
    workspace_member = get_object_or_404(WorkspaceMember,id=member_id)
    if workspace_obj == workspace_member.workspace:
    
        workspace_member.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def create_permissions(request):
    with open('main_perm.json', 'r', errors='ignore', encoding='UTF-8') as file:

        data = json.load(file)
        workspaces = WorkSpace.objects.all()
        for workspace in workspaces:
            members = WorkspaceMember.objects.filter(workspace=workspace)
            
            for member in members:
                for side_permission in data:
                    try:
                        member_permission = MemberPermission.objects.get(member=member,permission_name=side_permission['permission_name'])
                        for item in side_permission['items']:
                            try:
                                view_name = ViewName.objects.get(
                                    permission = member_permission,
                                    view_name=item['view_name']
                                
                                )
                                for method in side_permission['methods']:
                                    try:
                                        method_permission = MethodPermission.objects.get(view=view_name,method_name=method)
                                    except:
                                        method_permission = MethodPermission.objects.create(view=view_name,method_name=method)
                            except:

                                view_name = ViewName.objects.create(
                                    permission = member_permission,
                                    view_name=item['view_name']
                                
                                )
                                
                                for method in side_permission['methods']:
                          
                                    method_permission = MethodPermission.objects.create(view=view_name,method_name=method)
                    except:
                        member_permission =MemberPermission.objects.create(member=member,permission_name=side_permission['permission_name'])
                        for item in side_permission['items']:

                            view_name = ViewName.objects.create(
                                    permission = member_permission,
                                    view_name=item['view_name']
                                
                            )
                            for method in side_permission['methods']:
                          
                                method_permission = MethodPermission.objects.create(view=view_name,method_name=method)
    return Response(status=status.HTTP_200_OK)




class PermissionManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceUser]
    def get(self,request):

        workspace_id = request.GET.get("workspace_id")

        member_id = request.GET.get("member_id")
        workspace_member_obj =get_object_or_404(WorkspaceMember,id=member_id)
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        if request.user == workspace_obj.owner:
            serializer_data = [
                {
                    "id":permission.id,
                    "permission_name":permission.permission_name,
                    "permission_type":permission.permission_type
                } for permission in workspace_member_obj.permissions.all() if permission.permission_name == "project board"
            ]
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data
            })
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"permission denaid",
            "data":{}
        })
    

    def put(self,request,permission_id):
        data= request.data
        workspace_id= data.get("workspace_id")
        avatar_id =data.get("avatar_id",None)
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)

        permission_member_obj = get_object_or_404(MemberPermission, id=permission_id)
        if avatar_id:
            main_file = MainFile.objects.get(id=avatar_id)
            main_file.its_blong=True
            permission_member_obj.member.avatar= main_file
            permission_member_obj.member.save()
        if request.user == workspace_obj.owner:

            with open('main_perm.json', 'r', errors='ignore', encoding='UTF-8') as file:
                    permission_type = data.get("permission_type")
                

                    data = json.load(file)
                    for permission in data:
                        if permission['permission_name'] == permission_member_obj.permission_name:
                            for item in permission['items']:

                                try:
                                    view_permission_obj = permission_member_obj.view_names.get(view_name=item['view_name'])

                                    for perm in item['permissions']:
                                        
                                        if perm['type'] == permission_type:
                                            for method in perm['methods']:

                                                    method_obj= view_permission_obj.methods.get(method_name=method['method'])
                                         
                                       
                                                    method_obj.is_permission=method['status']
                                                    method_obj.save()
                                                 
                               
                                    
                                except:
                                    continue
                    
                    permission_member_obj.permission_type=permission_type
                    permission_member_obj.save()
                    return Response(status=status.HTTP_200_OK)




        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"permission denaid",
            "data":{}
        })
    

        


def create_permission_for_member (member_id,permissions):
  with open('main_perm.json', 'r', errors='ignore', encoding='UTF-8') as file:
            # Load the JSON data
                data = json.load(file)



                member = WorkspaceMember.objects.get(id=member_id)

                for side_permission in data:
                    main_permission_type="no access"
                    for permission in permissions:
                        if permission['permission_name'] == side_permission['permission_name']:
                            main_permission_type= permission['permission_type']

                    try:
                        member_permission =MemberPermission.objects.get(member=member,permission_name=side_permission['permission_name'])
                        for item in side_permission['items']:
                            try:
                                view_name = ViewName.objects.get(
                                    permission = member_permission,
                                    view_name=item['view_name']

                                )
                                for method in side_permission['methods']:
                                    try:

                                        method_permission = MethodPermission.objects.get(view=view_name,method_name=method,permission_type=main_permission_type)

                                    except:
                                        method_permission = MethodPermission.objects.create(view=view_name,method_name=method,permission_type=main_permission_type)
                                    for permission in item['permissions']:
                                        if permission['type'] == main_permission_type:
                                            for method_type in permission['methods']:
                                                if method_type['method'] == method_permission.method_name:
                                                    method_permission.is_permission =method_type['status']
                                                    method_permission.save()

                            except:

                                view_name = ViewName.objects.create(
                                    permission = member_permission,
                                
                                    view_name=item['view_name']
                                
                                )
                                
                                for method in side_permission['methods']:
                          
                                    method_permission = MethodPermission.objects.create(view=view_name,method_name=method)
                                    for permission in item['permissions']:
                                        if permission['type'] == main_permission_type:
                                            for method_type in permission['methods']:
                                                if method_type['method'] == method_permission.method_name:
                                                    method_permission.is_permission = method_type['status']
                                                    method_permission.save()
                    except:
                        member_permission =MemberPermission.objects.create(member=member,permission_name=side_permission['permission_name'],permission_type=main_permission_type)
                        for item in side_permission['items']:

                            view_name = ViewName.objects.create(
                                    permission = member_permission,
                                    view_name=item['view_name']
                                
                            )
                            for method in side_permission['methods']:
                          
                                method_permission = MethodPermission.objects.create(view=view_name,method_name=method)
                                for permission in item['permissions']:
                                    if permission['type'] == main_permission_type:
                                        for method_type in permission['methods']:
                                            if method_type['method'] == method_permission.method_name:
                                                method_permission.is_permission = method_type['status']
                                                method_permission.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_workspace_invitation (request):
    data =request.data

    workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
    member_obj =   WorkspaceMember.objects.get(user_account = request.user,workspace=workspace_obj)

    is_accepted = data.get("is_accepted")
    if is_accepted:
        member_obj.is_accepted= is_accepted
        member_obj.save()
        if workspace_obj.is_team_bonos:
            workspace_obj.wallet.balance += 30000
            workspace_obj.wallet.save()


        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت انجام شد",
            "data":{
                "is_accepted":is_accepted
            }
        })

    member_obj.delete()
    if WorkSpace.objects.filter(owner=request.user).exists():
        request.user.current_workspace_id = WorkSpace.objects.filter(owner=request.user).first().id

    else:
        if WorkspaceMember.objects.filter(user_account=request.user).exists():
            request.user.current_workspace_id=WorkspaceMember.objects.filter(user_account=request.user).first().id
        else:
            request.user.current_workspace_id =0
    request.user.save()
    return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت انجام شد",
            "data":{
                "is_accepted":is_accepted
            }
        })




@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_expert_users(request):
    workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
    expert_user = [
        {
            "id": user.user_account.id,
            "fullname": user.user_account.fullname,
            "avatar_url": user.user_account.avatar_url(),
        }
        for user in workspace_obj.workspace_member.all()

    ]
    expert_user.append(
        {
            "id": workspace_obj.owner.id,
            "fullname": workspace_obj.owner.fullname,
            "avatar_url": workspace_obj.owner.avatar_url(),
        }
    )
    return Response(status=status.HTTP_200_OK, data={
        "status": True,
        "message": "success",
        "data": expert_user
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_manager_users(request):
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
    # if request.user == workspace_obj.owner:
        manager_users = [
            {
                "id": workspace_obj.owner.id,
                "fullname": workspace_obj.owner.fullname,
                "avatar_url": workspace_obj.owner.avatar_url(),
                "self": request.user == workspace_obj.owner
            }
        ]

        for user in workspace_obj.workspace_member.all():
            for permission in user.permissions.all():
                if permission.permission_name == "project board":
                    if permission.permission_type == "manager":
                        manager_users.append(

                            {
                                "id": user.user_account.id,
                                "fullname": user.user_account.fullname,
                                "avatar_url": user.user_account.avatar_url(),
                                "self":user.user_account == request.user
                            }
                        )



        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "success",
            "data": manager_users
        })
    # return Response(status=status.HTTP_400_BAD_REQUEST, data={
    #     "status": False,
    #     "message": "عدم دسترسی",
    #     "data": {}
    # })




class WorkSpaceMemberManger(APIView):
    permission_classes= [IsAuthenticated]


    def get(self,request,member_id=None):
        if member_id:
            member_workspace = get_object_or_404(WorkspaceMember,id=member_id)
            serializer_data =WorkSpaceMemberSerializer(member_workspace)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)

        workspace_member = WorkspaceMember.objects.filter(workspace= workspace_obj)
        member_data =[]
        if workspace_obj.owner != request.user:
            data = UserSerializer(workspace_obj.owner).data
            data['fullname'] = workspace_obj.owner.fullname
            data['jtime'] = workspace_obj.owner.jtime()
            member_data.append(
                {
                    "user_account":data,
                    "type":"owner"
                }

            )


        for member in workspace_member:
            is_register= member.is_accepted
            main_data =WorkSpaceMemberSerializer(member).data
            main_data['user_account']['is_register']  = member.is_accepted
            member_data.append(main_data)


        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":member_data
        })


    def post(self,request):

        request.data['workspace_id'] = request.user.current_workspace_id
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        if workspace_obj.owner == request.user:
            permissions = request.data.get("permissions")
            serializer_data = WorkSpaceMemberSerializer(data= request.data)

            if serializer_data.is_valid():
                new_member = serializer_data.save()



                return Response(status=status.HTTP_201_CREATED,data={
                    "status":True,
                    "message":"کاربر با موفقیت اضافه شد",
                    "data":serializer_data.data
                })
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"validation error",
                "data":serializer_data.errors
            })
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"you dont have permission dont try",
            "data":{},
        })

    def put(self,request,member_id):
        member_obj = get_object_or_404(WorkspaceMember,id=member_id)
        data = request.data
        permission_list= data.get("permission_list")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        avatar_id =data.get("avatar_id",None)
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        if workspace_obj.owner == request.user:

            for permission_item in permission_list:
                permission_member_obj= MemberPermission.objects.get(id=permission_item['id'])
                with open('main_perm.json', 'r', errors='ignore', encoding='UTF-8') as file:
                    permission_type = permission_item["permission_type"]

                    data = json.load(file)
                    for permission in data:
                        if permission['permission_name'] == permission_member_obj.permission_name:
                            for item in permission['items']:

                                # try:
                                    view_permission_obj = permission_member_obj.view_names.get(view_name=item['view_name'])

                                    for perm in item['permissions']:

                                        if perm['type'] == permission_type:
                                            for method in perm['methods']:
                                                method_obj = view_permission_obj.methods.get(method_name=method['method'])

                                                method_obj.is_permission = method['status']
                                                method_obj.save()



                                # except:
                                #     continue

                    permission_member_obj.permission_type = permission_type
                    permission_member_obj.save()
            if avatar_id:
                main_file = MainFile.objects.get(id=avatar_id)
                main_file.its_blong=True
                main_file.save()
                member_obj.user_account.avatar=main_file
                member_obj.user_account.save()
            member_obj.first_name = first_name
            member_obj.last_name = last_name
            member_obj.fullname = f"{first_name} {last_name}"
            member_obj.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":WorkSpaceMemberSerializer(member_obj).data
            })
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"you dont have permission dont try!!",
            "data":{}
        })


    def delete(self,request,member_id):
        workspace_obj  = WorkSpace.objects.get(id=request.user.current_workspace_id)
        if request.user == workspace_obj.owner :
            workspace_member = get_object_or_404(WorkspaceMember,id=member_id)
            workspace_member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN, data={
            "status": False,
            "message": "you dont have permission dont try!!",
            "data": {}
        })
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_text_workspace_invite(request):
    workspace_obj = WorkSpace.objects.get(id =request.user.current_workspace_id)

    text = f"{workspace_obj.owner.fullname} شما را به کسب کار {workspace_obj.title} دعوت کرده است"
    return Response(
        status=status.HTTP_200_OK,
        data={
            "status":True,
            "message":"success",
            "data":{
                "text":text
            }
        }
    )

from ProjectManager.models import Project,CheckList

def calculate_user_performance(project_id):
    """
    Calculate the average performance percentage (1-100) for each user
    based on their completed checklists.
    """
    # Get all users with their completed checklists
    project_obj =Project.objects.get(id=project_id)
    users_with_performance = (
        CheckList.objects
        .filter(task__project=project_obj)  # Only completed checklists
        .values('responsible_for_doing')  # Group by user
        .annotate(
            total_tasks=Count('id'),  # Total completed tasks
            average_difficulty=Avg('difficulty'),  # Average difficulty
            total_time=Sum(
                (timezone.now() - timezone.now())  # Placeholder for time calculation
            )  # Placeholder for total time
        )
    )

    # Calculate performance percentage for each user
    performance_data = []
    for user_data in users_with_performance:
        user_id = user_data['responsible_for_doing']
        total_tasks = user_data['total_tasks']
        average_difficulty = user_data['average_difficulty']

        # Calculate performance percentage (N * E, scaled to 1-100)
        performance_percentage = min(max((total_tasks * average_difficulty) / 5 * 20, 1), 100)

        performance_data.append({
            'user_id': user_id,
            'total_tasks': total_tasks,
            'average_difficulty': round(average_difficulty, 2),
            'performance_percentage': round(performance_percentage, 2)
        })

    return performance_data
from WorkSpaceChat.models import  GroupMessage
@api_view(['GET'])
@permission_classes([AllowAny])
def create_group_message(request):
    performance_data = calculate_user_performance(project_id=19)

    # Print results
    for data in performance_data:
        print(f"User ID: {data['user_id']}")
        print(f"Total Tasks: {data['total_tasks']}")
        print(f"Average Difficulty: {data['average_difficulty']}")
        print(f"Performance Percentage: {data['performance_percentage']}%")
        print("-" * 30)
    # from django.db.models import Q
    # from WorkSpaceManager.models import  WorkSpace
    # from WorkSpaceChat.models import GroupMessage
    # workspace_objs = WorkSpace.objects.all()
    #
    # for workspace_obj in workspace_objs:
    #     members = list(WorkspaceMember.objects.filter(workspace=workspace_obj).values_list('user_account', flat=True))
    #
    #     # Create a group for the workspace owner and each member
    #     for member in members:
    #         if not GroupMessage.objects.filter(
    #                 workspace=workspace_obj,
    #                 members=workspace_obj.owner
    #         ).filter(members=member).exists():
    #             group_message = GroupMessage.objects.create(workspace=workspace_obj)
    #             group_message.members.set([workspace_obj.owner, member])
    #
    #     # Create a group for every unique pair of members
    #     for i in range(len(members)):
    #         for j in range(i + 1, len(members)):
    #             user1 = members[i]
    #             user2 = members[j]
    #
    #             # Check if a group already exists with exactly these two members
    #             if not GroupMessage.objects.filter(
    #                     workspace=workspace_obj
    #             ).filter(members=user1).filter(members=user2).exists():
    #                 group_message = GroupMessage.objects.create(workspace=workspace_obj)
    #                 group_message.members.set([user1, user2])

    return Response(status=status.HTTP_200_OK)


class WorkSpaceMemberArchive(APIView):
    def get(self,request):
        workspace_id = request.user.current_workspace_id
        workspace_obj = WorkSpace.objects.get(id=workspace_id)
        workspace_member = WorkspaceMember.all_objects.filter(is_deleted=True,workspace=workspace_obj)
        serializer_data = WorkSpaceMemberSerializer(workspace_member,many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت انجام شد",
            "data":serializer_data.data
        })
    def put(self,request,member_id):
        try:
            member_obj= WorkspaceMember.all_objects.get(id=member_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        member_obj.restore()
        member_obj.save()
        serializer_data = WorkSpaceSerializer(member_obj)
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"با موفقیت انجام شد ",
            "data":serializer_data.data
        })




@api_view(["GET"])
@permission_classes([AllowAny])
def create_users_to_jadoo(request):
    user_objs = UserAccount.objects.all()
    jadoo_base_url = os.getenv("JADOO_BASE_URL")
    base_url = os.getenv("BASE_URL")
    url = f"{jadoo_base_url}/user/auth/createBusinessUser"
    for user in user_objs:
            print(user.phone_number)
            if user.phone_number:

                payload = {
                    "mobile": user.phone_number,

                    "password": "w33rxss",

                }
                response_data = requests.post(url=url,data=payload)
                data =response_data.json()
                print(response_data)
                user.refrence_id = int(data['data']['id'])
                user.refrence_token = data['data']['token']
                print(data)
                user.save()


    return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([AllowAny])
def create_workspace_to_jadoo(request):
    jadoo_base_url = os.getenv("JADOO_BASE_URL")
    base_url = os.getenv("BASE_URL")
    workspaces = WorkSpace.objects.all()
    for workspace in workspaces:

        url = f"{jadoo_base_url}/workspace/store"
        print(workspace.owner.refrence_token)
        headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {workspace.owner.refrence_token}"
        }
        payload = {

            "workspaceId": workspace.id,
            # "industrialActivityId": workspace.industrialactivity.refrence_id,
            "bio": workspace.business_detail,
            "avatar": "",
            "name": workspace.title,
            "username": workspace.jadoo_brand_name
        }
        print(workspace.business_detail)
        if workspace.industrialactivity:
            payload['industrialActivityId'] = workspace.industrialactivity.refrence_id
        if workspace.state:
            payload["stateId"]: workspace.state.refrence_id
        if workspace.city:
            payload["cityId"]: workspace.city.refrence_id

        try:
            payload['avatar'] = f"{base_url}{workspace.avatar.file.url}"
        except:
            pass
        response_data = requests.post(url=url, headers=headers, json=payload)


        response_data_main = response_data.json()['data']
        workspace.jadoo_workspace_id = response_data_main['id']
        workspace.save()
    return Response(status=status.HTTP_200_OK)


class WorkSpacePermissionManager(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,permission_id=None):
        if permission_id:
            permission_obj = get_object_or_404(WorkSpacePermission, id=permission_id)
            serializer_data = WorkSpacePermissionSerializer(permission_obj)
            return Response(
                status=status.HTTP_202_ACCEPTED,
                data={
                    "status": True,
                    "message": "موفق",
                    "data": serializer_data.data
                }
            )
        workspace_id = request.user.current_workspace_id
        permission_objs = WorkSpacePermission.objects.filter(workspace_id=workspace_id)
        serializer_data = WorkSpacePermissionSerializer(permission_objs,many=True)

        return Response(
            status=status.HTTP_202_ACCEPTED,
            data={
                "status": True,
                "message": "موفق",
                "data": serializer_data.data
            }
        )
    def put(self,request,permission_id):
        permission_obj = get_object_or_404(WorkSpacePermission, id=permission_id)
        data = request.data
        is_active = data.get("is_active")
        permission_obj.is_active = is_active
        permission_obj.save()
        serializer_data = WorkSpacePermissionSerializer(permission_obj)
        return Response(
            status=status.HTTP_202_ACCEPTED,
            data={
                "status": True,
                "message": "با موفقیت بروزرسانی شد ",
                "data": serializer_data.data
            }
        )



@api_view(['GET'])
@permission_classes([AllowAny])
def get_message(request):
    from collections import defaultdict
    from WorkSpaceChat.models import TextMessage
    from django.db.models import F
    import locale
    from WorkSpaceChat.serializers import TextMessageSerializer
    import jdatetime
    from rest_framework.response import Response
    from rest_framework import status

    # Set locale for Persian language (move outside loop)
    locale.setlocale(locale.LC_ALL, 'fa_IR')

    messages = TextMessage.objects.all().order_by("created_at")

    # Group messages by date
    grouped_data = defaultdict(list)
    for msg in messages:
        # Convert Gregorian date to Jalali
        jalali_date = jdatetime.datetime.fromgregorian(date=msg.created_at.date())

        # Format Jalali date
        formatted_date_persian = jalali_date.strftime("%d %B")

        # Group messages
        grouped_data[formatted_date_persian].append(TextMessageSerializer(msg).data)

    # Convert grouped data to required format
    result = [{"date": date, "messages": msgs} for date, msgs in grouped_data.items()]

    # Return JSON response
    return Response(result, status=status.HTTP_200_OK)

