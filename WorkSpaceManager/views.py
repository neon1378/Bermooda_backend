from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from .models import *
from rest_framework.decorators import parser_classes
from django.shortcuts import get_object_or_404
import os 
import json
from Notification.models import Notification
from .serializers import WorkSpaceSerializer
import requests
from dotenv import load_dotenv
from core.permission import IsAccess,IsWorkSpaceUser
load_dotenv()
from WalletManager.models import Wallet
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_sub_category(request,category_id):
        main_category = get_object_or_404(MainCategory,id=category_id)

        categorys =[
                {
                    "title":category.title,
                    "id":category.id,
                    "isDisable":category.isDisable,
                    "icon":category.icon
                }for category in main_category.sub_category.all()
            ]

        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":categorys
        })
class WorkspaceManager(APIView):
    permission_classes = [IsAuthenticated]
    jadoo_base_url = os.getenv("JADOO_BASE_URL")

    def delete(self,request,workspace_id):
        workspace_obj =get_object_or_404(WorkSpace,id=workspace_id)
        workspace_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get(self,request,workspace_id=None):
        if workspace_id:
            workspace_obj= get_object_or_404(WorkSpace,id=workspace_id)
            if workspace_obj.owner == request.user:

                categorys =[
                    {
                        "title":category.title,
                        "id":category.id,
                        "isDisable":category.isDisable,
                        "icon":category.icon,
                        "selected": category == workspace_obj.main_category
                    }for category in MainCategory.objects.all()
                ]
                serializer_data =WorkSpaceSerializer(workspace_obj).data
                serializer_data['category'] = categorys
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
            categorys =[
                    {
                        
                        "title":category.title,
                        "id":category.id,
                        "isDisable":category.isDisable,
                        "icon":category.icon,
                        "sub_category":[],
                        "selected": category == workspace_obj.main_category
                    }for category in MainCategory.objects.all()
                ]
            
            for category in categorys:
                main_category = MainCategory.objects.get(id=category['id'])
                for sub_category in main_category.sub_category.all():
                    category['sub_category'].append(
                        {
                            "title":sub_category.title,
                            "id":sub_category.id,
                            "isDisable":sub_category.id,
                            "icon":sub_category.id,
                            "selected" : sub_category == workspace_obj.sub_category
                        }
                    )

            data['category'] = categorys
        return Response(status=status.HTTP_200_OK,data=serializer_data)
    def put(self,request,workspace_id):
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        data=request.data
        reference_sub_category = data.get("reference_sub_category")
        reference_category = data.get("reference_category")
        avatar_id = data.get("avatar_id",None)


        serializer_data =WorkSpaceSerializer(workspace_obj,data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            
            workspace_obj.is_authenticated=True
            workspace_obj.main_category_id =reference_category
            workspace_obj.sub_category_id =reference_sub_category
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
                new_wallet = Wallet(balance=100000,workspace=workspace_obj)
                new_wallet.save()
            if workspace_obj.is_authenticated == False:
                try:
                    url = f"{self.jadoo_base_url}/workspace/store"
                    headers = {
                        "content-type":"application/json",
                        "Authorization":f"Bearer {request.user.refrence_token}"
                    }
                    payload = {
                        "mainCategoryId":workspace_obj.main_category.reference_id,
                        "subCategoryId":workspace_obj.sub_category.reference_id,
                        "cityId":workspace_obj.state.refrence_id,
                        "stateId":workspace_obj.city.refrence_id,
                        "name":workspace_obj.title,
                        "username":workspace_obj.jadoo_brand_name,
                        "workspaceId":workspace_obj.id,
                        "bio":workspace_obj.business_detail,

                    }
        
                    response = requests.post(url=url,json=payload,headers=headers)
                    workspace_obj.jadoo_workspace_id= response.json()['id']
                except:
                    pass
      
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
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vc2VydmVyLmphZG9vLmFwcC9hcGkvdjEvdXNlci9hdXRoL2NyZWF0ZUJ1c2luZXNzVXNlciIsImlhdCI6MTczOTM1NDkzNCwiZXhwIjoxNzQwNTY0NTM0LCJuYmYiOjE3MzkzNTQ5MzQsImp0aSI6InliMWp5YWNOWWRBMkxwejMiLCJzdWIiOiI1MiIsInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.5Sbt2iZhax9pvd4bx8-BBgHn7C2UU1PljKhdYq4rpME"
    main_cat__url = f"{jadoo_base_url}/maincategory/getCategories"
    headers = {
                "Authorization":f"Bearer {token}" 
        }
    response =requests.get(url=main_cat__url,headers=headers)
    for main_cat in response.json()['data']:
        new_min_cat =MainCategory(
            reference_id = main_cat['id'],
            title = main_cat['title'],
            icon = main_cat['icon'],
            status = main_cat['status'],
            isDisable = False,
            isMedia = main_cat['isMedia']
        )
        new_min_cat.save()

        url_sub_cat = f"{jadoo_base_url}/maincategory/getAllSubCategory?parent_id={main_cat['id']}"
        response_sub_cat =requests.get(url=url_sub_cat,headers=headers)
        try:
            for sub_cat in response_sub_cat.json()['data']:
                new_sub_cat = SubCategory(
                    main_category = new_min_cat,
                    reference_id =sub_cat['id'],
                    title = sub_cat['title'],
                    icon = sub_cat['icon'],
                    isDisable= False,
                    isMedia = sub_cat['isMedia'],
                    status= sub_cat['status'],
                )
                new_sub_cat.save()
        except:
            pass
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
                } for permission in workspace_member_obj.permissions.all()
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
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        print(workspace_obj.owner == request.user)
        if request.user == workspace_obj.owner:

            with open('main_perm.json', 'r', errors='ignore', encoding='UTF-8') as file:
                    permission_type = data.get("permission_type")
                
                    permission_member_obj = get_object_or_404(MemberPermission,id=permission_id)
           
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
    

        


def create_permission_for_member (member_id):
  with open('main_perm.json', 'r', errors='ignore', encoding='UTF-8') as file:
            # Load the JSON data
                data = json.load(file)


   
                member = WorkspaceMember.objects.get(id=member_id)
     
                for side_permission in data:
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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_workspace_invitation (request,notification_id=None):
    data =request.data
    if notification_id:
        notification_obj = get_object_or_404(Notification,id=notification_id)
        
        member_obj =   notification_obj.related_object
        if member_obj.user_account == request.user:
            is_accepted = data.get("is_accepted")
            if is_accepted:
                member_obj.is_accepted= is_accepted
                member_obj.save()
                notification_obj.delete()
                return Response(status=status.HTTP_200_OK)

            member_obj.delete()
            notification_obj.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"access denaid",
            "data":{}
        })
    return Response(status=status.HTTP_400_BAD_REQUEST,data={
        "status":False,
        "message":"notification is required",
        "data":{}
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_manager_users(request):
    workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
    if request.user == workspace_obj.owner:
        manager_users = [

        ]
        for user in workspace_obj.workspace_member.all():
            for permission in user.permissions.all():
                if permission == "project board":
                    if permission.permission_type == "manager":
                        manager_users.append(

                            {
                                "id": user.user_account.id,
                                "fullname": user.user_account.fullname,
                                "avatar_url": user.user_account.avatar_url()
                            }
                        )
                        break
                    else:
                        break
        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "success",
            "data": manager_users
        })
    return Response(status=status.HTTP_400_BAD_REQUEST, data={
        "status": False,
        "message": "عدم دسترسی",
        "data": {}
    })