from logging import raiseExceptions

from django.shortcuts import render


from .serializers import *
from .models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.widgets import pagination
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from WorkSpaceManager.models import WorkspaceMember
from WorkSpaceManager.serializers import WorkSpaceMemberSerializer
from rest_framework.decorators import api_view,permission_classes
from core.permission import IsWorkSpaceMemberAccess


# Create your views here.


class FolderManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,slug=None):
        page_number = request.GET.get("page_number",1)
        workspace_obj =WorkSpace.objects.get(id=request.user.current_workspace_id)
        if slug:
            folder_obj = get_object_or_404(Folder,slug=slug)
            serializer_data =  FolderSerializer(folder_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })

        if request.user == workspace_obj.owner:
            folder_objs = Folder.objects.filter(workspace=workspace_obj)
        else:
            folder_objs = []
            for folder in Folder.objects.filter(workspace=workspace_obj):
                if request.user in folder.members.all():
                    folder_objs.append(folder)

        per_page_count= request.GET.get("per_page_count",20)
        pagination_data = pagination(query_set=folder_objs,page_number=page_number,per_page_count=per_page_count)
        pagination_data['list'] = FolderSerializer(pagination_data['list'],many=True).data

        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":pagination_data['list'],
            "extra":{
                "count": pagination_data['count'],
                "next": pagination_data['next'],
                "previous": pagination_data['previous'],
            }
        })
    def post(self,request):
        request.data['workspace_id'] = request.user.current_workspace_id
        serializer_data = FolderSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت ثبت شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.errors
        })
    def put(self,request,slug):
        folder_obj = get_object_or_404(Folder,slug=slug)
        request.data['workspace_id'] = folder_obj.workspace.id
        serializer_data = FolderSerializer(instance=folder_obj,data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.data
        })
    def delete(self,reqeust,slug):
        folder_obj = get_object_or_404(Folder,slug=slug)
        folder_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_folder_members (request):
    folder_slug = request.GET.get('folder_slug')
    page_number = request.GET.get('page_number',1)
    folder_obj = get_object_or_404(Folder,slug=folder_slug)
    workspace_members = WorkspaceMember.objects.filter(workspace=folder_obj.workspace,folder=folder_obj)
    paginate_data = pagination(query_set=workspace_members,page_number=page_number)



    paginate_data['list'] = WorkSpaceMemberSerializer(paginate_data['list'],many=True).data

    return Response(
        status=status.HTTP_200_OK,
        data= {
            "status":True,
            "message":"موفق",
            "data":paginate_data['list'],
            "extra":{
                "count":paginate_data['count'],
                "next":paginate_data['next'],
                "previous":paginate_data['previous'],
            }
        }
    )








class EmployeeRequestManager(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,slug=None):
        if slug:
            employee_request_obj = get_object_or_404(EmployeeRequest,slug=slug)
            serializer_data = EmployeeRequestSerializer(employee_request_obj).data
            return Response(
                status=status.HTTP_200_OK,data={
                    "status":True,
                    "message":"موفق",
                    "data":serializer_data
                }
            )

        page_number=request.GET.get('page_number',1)
        workspace_id = request.user.current_workspace_id
        workspace_obj = WorkSpace.objects.get(id=workspace_id)
        workspace_member = WorkspaceMember.objects.filter(workspace=workspace_obj, user_account=request.user).first()
        folder_obj = workspace_member.folder

        employee_request_objs = EmployeeRequest.objects.filter(folder=folder_obj)
        pagination_data = pagination(query_set=employee_request_objs,page_number=page_number)
        pagination_data['list'] = EmployeeRequestSerializer(pagination_data['list'],many=True).data
        return Response(
            status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":pagination_data['list'],
                "extra":{
                    "count": pagination_data['count'],
                    "next": pagination_data['next'],
                    "previous": pagination_data['previous'],
                }
            },
        )

    def post(self,request):
        request.data['requesting_user_id'] = request.user.id
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        serializer_data = EmployeeRequestSerializer(data=request.data,context={"user":request.user,"workspace_obj":workspace_obj})
        if serializer_data.is_valid(raise_exception=True):
            serializer_data.save()
            return Response(
                status=status.HTTP_200_OK,
                data = {
                "status":True,
                "message":"با موفقیت ثبت شد",
                "data":serializer_data.data
            }
            )
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer_data.errors)

    def put (self,request,slug):
        request_slug_obj = get_object_or_404(EmployeeRequest,slug=slug)
        request.data['requesting_user_id'] = request_slug_obj.requesting_user.id
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        serializer_data = EmployeeRequestSerializer(instance=request_slug_obj,data=request.data,context={"user":request.user,"workspace_obj":workspace_obj})
        if serializer_data.is_valid(raise_exception=True):
            serializer_data.save()
            return Response(
                status=status.HTTP_200_OK,
                data = {
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data
            }
            )
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer_data.errors)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_folder_categories(request):
    workspace_id = request.user.current_workspace_id
    workspace_obj= WorkSpace.objects.get(id=workspace_id)
    workspace_member = WorkspaceMember.objects.filter(workspace=workspace_obj,user_account=request.user).first()
    categories = FolderCategory.objects.filter(folder=workspace_member.folder)

    serializer_data = FolderCategorySerializer(categories,many=True).data
    return Response(
        status=status.HTTP_200_OK,
        data={
            "status":True,
            "message":"موفق",
            "data":serializer_data
        }
    )