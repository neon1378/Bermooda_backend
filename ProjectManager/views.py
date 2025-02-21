from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from UserManager.models import UserAccount
from rest_framework.permissions import IsAuthenticated
from .models import *
from rest_framework.authtoken.models import Token
import json
from .serializers import *
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from core.permission import IsWorkSpaceMemberAccess,IsWorkSpaceUser
from WorkSpaceManager.models import WorkSpace,WorkspaceMember
from dotenv import load_dotenv
import os
from MailManager.serializers import MemberSerializer
from Notification.views import create_notification
from django.db import transaction
load_dotenv()
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
#Project Manager Begin Bord Project 


class CategoryProjectManager(APIView):
    permission_classes =[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,category_id):
        category_obj = get_object_or_404(CategoryProject,id=category_id)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":{
                "id":category_obj.id,
                "title":category_obj.title,
                "color_code":category_obj.color_code
            }
        })
        
    def post(self,request):
        data = request.data
        project_obj = get_object_or_404(Project,id=data['project_id'])
        
        new_category_project =CategoryProject(
            title = data['title'],
            color_code = data['color_code'],
        )


        if project_obj.category_project.last().order != None:
            new_category_project.order = int(project_obj.category_project.last().order) +1 
        new_category_project.project=project_obj
        new_category_project.save()
        return Response(status =status.HTTP_201_CREATED,data={
            "status":True,
            "message":"succses",
            "data":{
                "id":new_category_project.id,
                "title":new_category_project.title,
                "color_code":new_category_project.color_code
            }
        })
    def put(self,request,category_id):
        data= request.data
        category_project_obj = get_object_or_404(CategoryProject,id=category_id)
        category_project_obj.title=data['title']
        category_project_obj.color_code=data['color_code']
        category_project_obj.save()
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"succses",
            "data":{
                "id":category_id,
                "title":category_project_obj.title,
                "color_code":category_project_obj.color_code,
            }
        })
        
    def delete(self,request,category_id):
        category_obj = get_object_or_404(CategoryProject,id=category_id)
        if not Task.objects.filter(category_task=category_obj).exists():
            category_obj.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if CategoryProject.objects.filter(project=category_obj.project).count() == 1:
                return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"امکان حذف وجود ندارد",
                    "data":{}
                })
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"ابتدا ستون را خالی کنید",
                    "data":{}
                })


class ProjectManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]
    


    def _get_member_progress(self,project,user):

        all_sub_task_completed= 0
        all_sub_tasks=0
        for task in project.task.filter(done_status=False):
            sub_task_completed = task.check_list.filter(status=True,responsible_for_doing=user).count()
            sub_tasks = task.check_list.filter(responsible_for_doing=user).count()
            all_sub_task_completed+=sub_task_completed
            all_sub_tasks +=sub_tasks
        

        progress_percentage = (all_sub_task_completed / all_sub_tasks * 100) if all_sub_tasks > 0 else 0
        return progress_percentage
    def get(self, request,project_id=None):
        

        if project_id:  
            project_obj = get_object_or_404(Project,id=project_id)
            serializer_data = ProjectSerializer(project_obj)
            for user in serializer_data.data['members']:
                user_account = UserAccount.objects.get(id=user['id'])
                user["progress_percentage"] =  self._get_member_progress(project=project_obj, user=user_account)
            return Response(status=status.HTTP_200_OK,data=serializer_data.data)
        department_id = request.GET.get("department_id",None)
        department_obj = get_object_or_404(ProjectDepartment,id=department_id)
        workspace_id  = request.GET.get('workspace_id')
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        if request.user == workspace_obj.owner or department_obj.manager == request.user:
            projects = Project.objects.filter(workspace=workspace_obj,department_id=department_id)
        else:

            project_workspace = Project.objects.filter(workspace=workspace_obj,department_id=department_id)


            projects =[]
            for pro in project_workspace:
                if request.user in pro.members.all():
                    projects.append(pro)


        serializer_data = ProjectSerializer(projects,many=True)
        for data in serializer_data.data:
            for user in data['members']:

                project_obj=Project.objects.get(id=data['id'])
                user_account = UserAccount.objects.get(id=user['id'])
                if user_account == workspace_obj.owner:
                    user['permission_type'] = "manager"
                else:
                    try:
                        member_workspace = WorkspaceMember.objects.get(workspace=workspace_obj,user_account=user_account)
                        for permission in member_workspace.permissions.all():
                            if permission.permission_name == "project board":
                                user['permission_type'] = permission.permission_type
                    except:
                        user['permission_type'] = "no access"
                user["progress_percentage"] = self._get_member_progress(project=project_obj, user=user_account)
        return Response(status=status.HTTP_200_OK, data={
            "status":True,
            "message":"موفقیت",
            "data":serializer_data.data
        })
    

        
    def post(self, request):


        serializer_data =ProjectSerializer(data=request.data)
        if serializer_data.is_valid():
            project_obj = serializer_data.save()
            for user in serializer_data.data['members']:
                user_account = UserAccount.objects.get(id=user['id'])
                user["progress_percentage"] =  self._get_member_progress(project=project_obj, user=user_account)
            return Response(status=status.HTTP_201_CREATED, data={
                "status":True,
                "message":"پروژ ه جدید با موفقیت ثبت شد",
                "data":serializer_data.data
            })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "لطفا اطلاعات رو به درستی وارد کنید",
            "data": serializer_data.errors
        })



    def put(self, request, project_id):

        # Fetch the project or return a 404 response
        project_obj = get_object_or_404(Project, id=project_id)
        serializer_data = ProjectSerializer(instance=project_obj,data=request.data)

        if serializer_data.is_valid():
            serializer_data.save()
            for user in serializer_data.data['members']:
                user_account = UserAccount.objects.get(id=user['id'])
                user["progress_percentage"] =  self._get_member_progress(project=project_obj, user=user_account)
            return Response(
                status=status.HTTP_202_ACCEPTED,
                data={
                    "status": True,
                    "message": "پروژه با موفقیت بروزرسانی شد",
                    "data":serializer_data.data
                }
            )

        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "لطفا اطلاعات رو به درستی وارد کنید",
            "data": serializer_data.errors
        })

            
    def delete(self,request,project_id):
        project_obj = get_object_or_404(Project,id=project_id)
        project_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





class TaskManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]
    import jdatetime

    def _convert_jalali_to_datetime(self,jalali_str):
        # Convert Persian numbers to English numbers
        date_part, time_part = jalali_str.split("T")
        year, month, day = map(int, date_part.split("/"))
        hour, minute = map(int, time_part.split(":"))
        return jdatetime.datetime(year, month, day, hour, minute)




    def task_url_creator(self, task_obj):
        """Generate file URLs for a given task."""
        base_url = os.getenv("BASE_URL", "")
        return [{"file_url": f"{base_url}{file.file.url}","id":file.id} for file in task_obj.main_file.all()]

    def get_task_data(self, task, project):
        """Serialize task data."""
        return {
            "id": task.id,
            "task_progress":task.task_progress(),
            "title": task.title,
           
            "description": task.description,
            "order": task.order,
 
            "category_task": task.category_task.title,
            "category_task_id": task.category_task.id,
            "check_list": [
                {
                    "id": item.id,
                    "title": item.title,
                    "status": item.status,
                    "label": {
                            "title": item.label.title,
                            "color_code": item.label.color_code,
                            } if item.label else {},
                    "responsible_for_doing":{
                            "fullname": item.responsible_for_doing.fullname,
                            "id": item.responsible_for_doing.id,
                            "avatar_url":item.responsible_for_doing.avatar_url(),
                           
                    } if item.responsible_for_doing else {},
                     
                    
         


                    "start_time": f"{item.date_to_start}T{item.time_to_start}",

                    # "time_to_start": item.time_to_start,
                    "end_time": f"{item.date_to_end}T{item.time_to_end}",
                    # "time_to_end": item.time_to_end,
                }
                for item in task.check_list.all()
            ],
            "file_urls": self.task_url_creator(task),
        }

    def get(self, request, project_id):
        """Retrieve tasks associated with a project."""
        project = get_object_or_404(Project, id=project_id)
        task_id = request.GET.get("task_id", None)
            
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            if task.done_status is not True:
                task_data = self.get_task_data(task, project)
                print(task_data["check_list"])
                task_data["check_list"].sort(key=lambda x: self._convert_jalali_to_datetime(x["end_time"]))
                print(task_data["check_list"])
                return Response(status=status.HTTP_200_OK, data={"status": True, "message": "success", "data": task_data})
            
            return Response(status=status.HTTP_200_OK, data={"status": True, "message": "task its completed", "data":{}})
            
        
        
        workspace_id = request.GET.get("workspace_id")
        workspace = get_object_or_404(WorkSpace, id=workspace_id)

        tasks = project.task.filter(done_status=False)
        task_data = [self.get_task_data(task, project) for task in tasks]
        for task in task_data:
            print(task['check_list'])
            task["check_list"].sort(key=lambda x: self._convert_jalali_to_datetime(x["end_time"]))
            print(task['check_list'])
        return Response(status=status.HTTP_200_OK, data={"status": True, "message": "success", "data": task_data})

    def post(self, request, project_id):

        """Create a new task."""
        project = get_object_or_404(Project, id=project_id)
        data = request.data
        task_reports = data.get("task_reports",[])
        check_list_data = data.pop("check_list",[])
        task_reports = data.pop("task_reports",[])
        file_ids = data.pop("file_id_list", [])
        category_id = data.pop("category_task")["id"]

        workspace_id = data.pop("workspace_id")
    
        for check_list in check_list_data:
            try:
                date_time_to_start = f"{check_list['date_to_start']} {check_list['time_to_start']}"
                date_time_to_end = f"{check_list['date_to_end']} {check_list['time_to_end']}"
                # print(date_time_to_start)
                date_time_start_obj = jdatetime.datetime.strptime(date_time_to_start, "%Y/%m/%d %H:%M")
                date_time_end_obj = jdatetime.datetime.strptime(date_time_to_end, "%Y/%m/%d %H:%M")
                if date_time_start_obj >= date_time_end_obj:
                    return Response(status=status.HTTP_400_BAD_REQUEST,data={
                        "status":False,
                        "message":f"در چک لیست {check_list['title']} تاریخ شروع و پایان درست نمیباشد"
                    })
            except:
                continue


            
        category = get_object_or_404(CategoryProject, id=category_id)


        task = Task.objects.create(
            **data,  category_task=category, project=project
        )
        
        # Associate files with the task
        MainFile.objects.filter(id__in=file_ids).update(its_blong=True)
        task.main_file.add(*MainFile.objects.filter(id__in=file_ids))

        # Set task order
        last_task = category.task_category.order_by("order").last()
        task.order = (last_task.order + 1) if last_task else 1
        task.save()

        # Create checklist items
        for item in check_list_data:
            user_id = item.get("responsible_for_doing",None)
            if user_id:
                responsible_user = get_object_or_404(UserAccount, id=item["responsible_for_doing"])
            else:
                responsible_user=request.user
            new_check_list =CheckList.objects.create(
                title=item["title"],
            
                date_to_start=item["date_to_start"],
                time_to_start=item["time_to_start"],
                date_to_end=item["date_to_end"],
                time_to_end=item["time_to_end"],
                responsible_for_doing=responsible_user,
                task=task,
        
            )
            if item['label_id']:
                new_check_list.label_id=item['label_id']['id']
            new_check_list.save()
        response_data = TaskSerializer(task).data
        for member in task.project.members.all():
            if member != request.user:
                title = f"وضیفه جدید"
                sub_title = f"وضیفه {task.title} توسط {request.user.fullname} به  پروژه شما اضافه شد"
                create_notification(related_instance=task,workspace=WorkSpace.objects.get(id=workspace_id),user=member,title=title,sub_title=sub_title,side_type="new_task")


# 
        for report_id in task_reports:
            report_obj = get_object_or_404(TaskReport,id=report_id)
            report_obj.task=task
            report_obj.save()
        channel_layer = get_channel_layer()
        event ={
            "type":"send_data"
        }
        async_to_sync(channel_layer.group_send)(f"{project.id}_amin",event)
        return Response(status=status.HTTP_201_CREATED, data={"status": True, "message": "تسک جدید با موفقیت ثبت شد", "data": response_data})

    def put(self, request):
        """Update an existing task."""
        data = request.data
        task = get_object_or_404(Task, id=data.get("task_id"))
        workspace_id = data.get("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        if data.get("change_done_status"):
            
            task.done_status = data["done_status"]
            task.save()
            return Response(status=status.HTTP_202_ACCEPTED, data={"status": True, "message": "Status updated"})

        # Update task fields
        task.title = data["title"]
        
        task.description = data["description"]







        existing_file_ids = list(task.main_file.values_list("id", flat=True))

        # Update associated files
        file_ids = data.get("file_id_list", [])
        MainFile.objects.filter(id__in=file_ids).update(its_blong=True)
        task.main_file.set(MainFile.objects.filter(id__in=file_ids))

        # Identify and delete files that are no longer associated with the task
        removed_file_ids = set(existing_file_ids) - set(file_ids)
        MainFile.objects.filter(id__in=removed_file_ids).delete()
        for member in task.project.members.all():
            title = f"بروزرسانی وظیفه"
            sub_title = f"وضیفه {task.title} توسط {request.user.fullname} بروزرسانی شد"
            create_notification(related_instance=task,workspace=workspace_obj,user=member,title=title,sub_title=sub_title,side_type="update_task")
        task.save()
        channel_layer = get_channel_layer()
        event ={
            "type":"send_data"
        }
        async_to_sync(channel_layer.group_send)(f"{task.project.id}_amin",event)
        return Response(status=status.HTTP_202_ACCEPTED, data={"status": True, "message": "تسک با موفقیت آپدیت شد"})

    def delete(self, request):
        """Delete a task."""
        workspace_obj = get_object_or_404(WorkSpace,id=request.data.get("workspace_id",None))
        task = get_object_or_404(Task, id=request.data["task_id"])
        for member in task.project.members.all():
            
            title = f"حذف وضیظه"
            sub_title = f"وضیفه {task.title} توسط {request.user.fullname} حذف شد"
            create_notification(related_instance=task,workspace=workspace_obj,user=member,title=title,sub_title=sub_title)
        task.delete()
        channel_layer = get_channel_layer()
        event ={
            "type":"send_data"
        }
        async_to_sync(channel_layer.group_send)(f"{task.project.id}_amin",event)
        return Response(status=status.HTTP_204_NO_CONTENT, data={"status": True, "message": "Task deleted"})





class CheckListManager(APIView):
    permission_classes=[IsAuthenticated]
    def get (self,request,checklist_id_or_task_id):
        check_list_obj = CheckList.objects.filter(task_id=checklist_id_or_task_id)
        check_list_serializer = CheckListSerializer(check_list_obj,many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":check_list_serializer.data
        })
    def post(self,request,checklist_id_or_task_id):
        
        task_obj = get_object_or_404(Task,id=checklist_id_or_task_id)
        data = request.data
        print(data)
        label_id = data.get("label_id",None)
        title = data.get("title")
        responsible_for_doing = data.get("responsible_for_doing",None)
        date_to_start = data.get("date_to_start",None)
        time_to_start = data.get("time_to_start",None)
        date_to_end = data.get("date_to_end",None)
        time_to_end = data.get("time_to_end",None)
        check_list_obj = CheckList.objects.create(
            task=task_obj,
            title = title,
            date_to_start = date_to_start,
            time_to_start = time_to_start,
            date_to_end = date_to_end,
            time_to_end = time_to_end,
        )
        if label_id and label_id != {}:
            check_list_obj.label_id=label_id['id']
        if responsible_for_doing:
            check_list_obj.responsible_for_doing_id=responsible_for_doing
        
        check_list_obj.save()
        channel_layer = get_channel_layer()
        event ={
            "type":"send_data"
        }
        async_to_sync(channel_layer.group_send)(f"{task_obj.project.id}_amin",event)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":CheckListSerializer(check_list_obj).data
        })
    def put (self,request,checklist_id_or_task_id):
        data = request.data
        command = data.get("command")

        checklist_obj = get_object_or_404(CheckList,id=checklist_id_or_task_id)
        if command == "change check list status":
            print(request.user)
            print(checklist_obj.responsible_for_doing)
            if checklist_obj.responsible_for_doing == request.user:
                
                if data['status']:
                
                    checklist_obj.status=True
                else:
                    checklist_obj.status=False
                checklist_obj.save()
                return Response(status=status.HTTP_202_ACCEPTED,data={
                    "status":True,
                    "message":"success",
                    "data":{}
                })

            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"شما مجاز به تغییر وضعیت چک لیست نیستید",
                "data":{}
            })
        elif command == "edit check list":
            label_id = data.get("label_id",None)
            title = data.get("title")
            responsible_for_doing = data.get("responsible_for_doing",None)
            date_to_start = data.get("date_to_start",None)
            time_to_start = data.get("time_to_start",None)
            date_to_end = data.get("date_to_end",None)
            time_to_end = data.get("time_to_end",None)
            if label_id and label_id != {}:
                checklist_obj.label_id=label_id['id']
            if responsible_for_doing:
                checklist_obj.responsible_for_doing_id=responsible_for_doing
            
            checklist_obj.title =title
            checklist_obj.date_to_start =date_to_start
            checklist_obj.time_to_start =time_to_start
            checklist_obj.date_to_end =date_to_end
            checklist_obj.time_to_end =time_to_end
            checklist_obj.save()
            channel_layer = get_channel_layer()
            event = {
                "type": "send_data"
            }
            async_to_sync(channel_layer.group_send)(f"{checklist_obj.task.project.id}_amin", event)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":CheckListSerializer(checklist_obj).data
            })


    def delete(self,request,checklist_id_or_task_id):
        checklist_obj = get_object_or_404(CheckList,id=checklist_id_or_task_id)
        checklist_obj.delete()
        channel_layer = get_channel_layer()
        event = {
            "type": "send_data"
        }
        async_to_sync(channel_layer.group_send)(f"{checklist_obj.task.project.id}_amin", event)
        return Response(status=status.HTTP_204_NO_CONTENT)

        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_users(request,project_id):
    workspace_obj = get_object_or_404(WorkSpace,id=request.GET.get("workspace_id"))

    project_obj = Project.objects.get(id=project_id)
    user_list = [
        {

            "fullname": workspace_obj.owner.fullname,
            "id": workspace_obj.owner.id,
            "avatar_url": workspace_obj.owner.avatar_url(),
            "self": request.user == workspace_obj.owner
        }
    ]
    for member in project_obj.members.all():
        if member != workspace_obj.owner :
            user_list.append({

                "fullname": member.fullname,
                "id": member.id,
                "avatar_url": member.avatar_url(),
                "self": request.user == member
            }
            )
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"موفق",
        "data":user_list
    })

def test_html_page(request,project_id):


    token = Token.objects.get_or_create(user=request.user)[0]
    project_obj = Project.objects.get(id=project_id)
    

    return render(request,"ProjectManager/test.html",{"token":str(token),"project_obj":project_obj})



class LabelTaskManager(APIView):
    def label_serializer(self,label_obj):
        return {
            "order":label_obj.order,
            "title":label_obj.title,
            "color_code":label_obj.color_code,
            "id":label_obj.id
        }
    def get(self,request,label_id=None):
        project_id = request.GET.get("project_id")

        project_obj = get_object_or_404(Project,id=project_id)
        if label_id:
            label_obj = get_object_or_404(TaskLabel,id=label_id)
            serializer_data= self.label_serializer(label_obj=label_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data
            })
        
        label_objs =TaskLabel.objects.filter(project =project_obj)
        serializer_data = [
            self.label_serializer(label_obj=label_obj)
            for label_obj in label_objs
        ]

        return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data
        })
    def post(self,request):
        data= request.data
        project_id = data['project_id']

        project_obj = get_object_or_404(Project,id=project_id)

        new_label_obj = TaskLabel(
            project= project_obj,
            title=data['title'],
            color_code= data['color_code']
        )
        new_label_obj.save()
        label_objs = TaskLabel.objects.filter(project =project_obj).order_by("-id")
        order=1
        for label_obj in label_objs:
            label_obj.order = order
            label_obj.save()
            order+=1
        
        serializer_data= self.label_serializer(label_obj=new_label_obj)
        return Response(status=status.HTTP_201_CREATED,data={
            "status":True,
            "message":"success",
            "data":serializer_data
        })
    def put(self,request,label_id):
        data= request.data
        label_obj = get_object_or_404(TaskLabel,id=label_id)
        label_obj.title=data['title']
        label_obj.color_code=data['color_code']
  
        label_obj.save()
        serializer_data= self.label_serializer(label_obj=label_obj)
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"success",
            "data":serializer_data
        })
    

    def delete (self,request,label_id):

        label_obj = get_object_or_404(TaskLabel,id=label_id)
        label_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TaskReportManager(APIView):
    def get(self,request,report_id=None):
        data = request.data
        if report_id:
            report_obj = get_object_or_404(TaskReport,id=report_id)
            serializer_data = TaskReportSerializer(report_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        task_id = request.GET.get("task_id")
        task_obj = get_object_or_404(Task,id=task_id)
        report_objs = TaskReport.objects.filter(task=task_obj).order_by('-id')
        serializer_data = TaskReportSerializer(report_objs,many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":"True",
            "message":"success",
            "data":serializer_data.data
        })
    def post(self,request):

        data = request.data
        new_task_report = TaskReport(
                body=data['body'],
     
                
                creator = request.user
        )
        task_id = data.get("task_id",None)

        file_id_list = data.get("file_id_list",[])
        replay_id = data.get("replay_id",None)
        if task_id:
            task_obj = get_object_or_404(Task,id=task_id)
            new_task_report.task = task_obj
       
        if replay_id:
            new_task_report.replay_id=replay_id
        new_task_report.save()
        for file_id in file_id_list:
            main_file = MainFile.objects.get(id=file_id)
            main_file.its_blong = True
            main_file.save()
            new_task_report.file.add(main_file)
        serializer_data = TaskReportSerializer(new_task_report)
        return Response(status=status.HTTP_201_CREATED,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data
        })
    def put (self,request,report_id):
        data= request.data
        report_obj = get_object_or_404(TaskReport,id=report_id)
        report_obj.body= data['body']
        file_id_list = data.get("file_id_list",[])
        replay_id = data.get("replay_id",None)
        for file_id in file_id_list:
            main_file = MainFile.objects.get(id=file_id)
            main_file.its_blong = True
            main_file.save()
            report_obj.file.add(main_file)
        if replay_id:
            
            report_obj.replay_id=replay_id
        report_obj.save()
        serializer_data = TaskReportSerializer(report_obj)
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data
        })
    def delete (self,request,report_id):

        report_obj = get_object_or_404(TaskReport,id=report_id)

        report_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    







class ProjectDepartmentManager(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,department_id=None):
        if department_id:
            department_obj = get_object_or_404(ProjectDepartment,id=department_id)
            serializer_data = ProjectDepartmentSerializer(department_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        if workspace_obj.owner == request.user:
            department_objs= ProjectDepartment.objects.filter(workspace=workspace_obj)
            serializer_data = ProjectDepartmentSerializer(department_objs,many=True)

        else:

            department_list = ProjectDepartment.objects.filter(workspace=workspace_obj)
            department_objs = set()

            for department in department_list:
                if request.user == department.manager:
                    department_objs.add(department)
                else:
                    for project in department.project_department.all():
                        if request.user in project.members.all():
                            department_objs.add(department)
                            break
                
            department_objs=list(department_objs)
            serializer_data = ProjectDepartmentSerializer(department_objs,many=True)
        return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
    def post(self,request):
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        if workspace_obj.owner == request.user:
            request.data['workspace_id'] = request.user.current_workspace_id

            serializer_data = ProjectDepartmentSerializer(data=request.data)
            data= request.data





            if serializer_data.is_valid():
                serializer_data.save()

                return Response(status=status.HTTP_201_CREATED,data={
                    "status":True,
                    "message":"success",
                    "data":serializer_data.data
                })

            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"validation error",
                "data": serializer_data.errors
            })
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"عدم دسترسی",
            "data":{}
        })
    def put(self,request,department_id):
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        if workspace_obj.owner == request.user:
            department_obj = get_object_or_404(ProjectDepartment,id=department_id)
            request.data['workspace_id'] = department_obj.workspace.id

            serializer_data = ProjectDepartmentSerializer(data=request.data,instance=department_obj)
            if serializer_data.is_valid():
                serializer_data.save()
                return Response(status=status.HTTP_202_ACCEPTED,data={
                    "status":True,
                    "message":"success",
                    "data":serializer_data.data
                })
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"validation error",
                "data":serializer_data.errors
            })
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"عدم دسترسی",
            "data":{}
        })
    def delete(self,request,department_id):
        department_obj = get_object_or_404(ProjectDepartment,id=department_id)
        department_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


