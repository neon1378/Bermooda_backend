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


        pagination_data = pagination(query_set=folder_objs,page_number=page_number)
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
            "data":serializer_data.data
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
    paginate_data = pagination(query_set=folder_obj.members.all(),page_number=page_number)
    workspace_member_list = [

    ]
    for member in paginate_data['list']:
        if member == folder_obj.workspace.owner:
            workspace_member_list.append(
                {
                    "user_account":{
                        "id":member.id,
                        "full_name":member.full_name,

                    },
                    "type":"owner"
                }
            )
        else:
            workspace_member_obj = WorkspaceMember.objects.get(user_account=member,workspace=folder_obj.workspace)
            serializer_data = WorkSpaceMemberSerializer(workspace_member_obj).data
            serializer_data['type'] ="member"
            workspace_member_list.append(serializer_data)
    paginate_data['list'] = workspace_member_list
    return Response(
        status=status.HTTP_200_OK,
        data= {
            "status":True,
            "message":"موفق",
            "data":paginate_data['iist'],
            "extra":{
                "count":paginate_data['count'],
                "next":paginate_data['next'],
                "previous":paginate_data['previous'],
            }
        }
    )





