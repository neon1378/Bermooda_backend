from django.shortcuts import render
from rest_framework import status
from core.widgets import  pagination
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from UserManager.models import UserAccount
from rest_framework.permissions import IsAuthenticated
from .models import *
from core.widgets import  persian_to_gregorian
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
from core.widgets import create_reminder
#Project Manager Begin Bord Project 


def create_notify_message(message,related_instance,project_id,creator_id):
    content_type = ContentType.objects.get_for_model(related_instance.__class__)
    message_obj = ProjectMessage.objects.create(
        message_type="notification",
        content_type=content_type,
        object_id=related_instance.id,
        body=message,
        project_id=project_id,
        creator_id=creator_id
    )
    channel_layer = get_channel_layer()
    event = {
                "type": "send_a_message",
                "message_id": message_obj.id

            }

    async_to_sync(channel_layer.group_send)(f"{project_id}_gp_project", event)
    return True


def create_reminde_a_task(chek_list):
    if chek_list.date_time_to_start_main:
        title = "یاد آوری وظیفه"
        short_text = ' '.join(chek_list.title.split()[:15]) + ('...' if len(chek_list.title.split()) > 15 else '')
        sub_title = f"وقت شروع وظیفه  {short_text} هست "
        create_reminder(related_instance=chek_list, remind_at=chek_list.date_time_to_start_main, title=title, sub_title=sub_title)
    elif chek_list.date_time_to_end_main:
        title = "یاد آوری وظیفه",
        short_text = ' '.join(chek_list.title.split()[:15]) + ('...' if len(chek_list.title.split()) > 15 else '')
        sub_title = f"تایم انجام وظیفه {short_text} تمام شده است  "
        create_reminder(related_instance=chek_list, remind_at=chek_list.date_time_to_start_main, title=title,
                        sub_title=sub_title)

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

        try:
            if project_obj.category_project.last().order != None:
                new_category_project.order = int(project_obj.category_project.last().order) +1
        except:
            new_category_project.order =1

        new_category_project.project=project_obj
        new_category_project.save()
        channel_layer = get_channel_layer()
        event = {
            "type": "send_event_task_list",
            "project_id": new_category_project.project.id
        }

        async_to_sync(channel_layer.group_send)(f"{new_category_project.project.id}_gp_project", event)
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
        channel_layer = get_channel_layer()

        event = {
            "type": "send_event_task_list",
            "project_id": category_project_obj.project.id
        }
        async_to_sync(channel_layer.group_send)(f"{category_project_obj.project.id}_gp_project", event)
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
            first_category= CategoryProject.objects.filter(project=category_obj.project).last()
            if first_category == category_obj:
                return Response(status=status.HTTP_400_BAD_REQUEST,data={
                    "status":False,
                    "message":"امکان حذف وجود ندارد",
                    "data":{}
                })

            project_id = category_obj.project.id
            category_obj.delete()
            channel_layer = get_channel_layer()
            event = {
                "type": "send_event_task_list",
                "project_id": project_id
            }


            async_to_sync(channel_layer.group_send)(f"{project_id}_gp_project", event)
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




        progress_percentage = project.calculate_user_performance(user_id=user.id)
        return progress_percentage['performance_percentage']
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
        workspace_id  = request.user.current_workspace_id
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        if request.user == workspace_obj.owner :
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
                        member_workspace = WorkspaceMember.all_objects.get(workspace=workspace_obj,user_account=user_account)
                        user['fullname']= member_workspace.fullname
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
        request.data['workspace_id'] =request.user.current_workspace_id

        serializer_data =ProjectSerializer(data=request.data,context={"user":request.user})
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
        request.data['workspace_id'] =request.user.current_workspace_id
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

            "file_urls": self.task_url_creator(task),
        }

    def get(self, request, project_id):
        """Retrieve tasks associated with a project."""
        project = get_object_or_404(Project, id=project_id)
        task_id = request.GET.get("task_id", None)

        if task_id:
            task = get_object_or_404(Task, id=task_id)
            # if task.done_status is not True:
            task_data = self.get_task_data(task, project)

            return Response(status=status.HTTP_200_OK, data={"status": True, "message": "success", "data": task_data})

            # return Response(status=status.HTTP_200_OK, data={"status": True, "message": "task its completed", "data":{}})



        workspace_id = request.user.current_workspace_id
        workspace = get_object_or_404(WorkSpace, id=workspace_id)

        tasks = project.task.filter(done_status=False)
        task_data = [self.get_task_data(task, project) for task in tasks]

        return Response(status=status.HTTP_200_OK, data={"status": True, "message": "success", "data": task_data})

    def post(self, request, project_id):

        """Create a new task."""
        project = get_object_or_404(Project, id=project_id)
        data = request.data
        data.pop("task_reports")
        check_list_data = data.pop("check_list",[])

        file_ids = data.pop("file_id_list", [])
        category_id = data.pop("category_task")["id"]

        workspace_id = data.pop("workspace_id",request.user.current_workspace_id)

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
            date_to_start = item.get("date_to_start",None)
            time_to_start = item.get("time_to_start",None)
            date_to_end = item.get("date_to_end",None)
            time_to_end = item.get("time_to_end",None)
            file_id_list = item.get("file_id_list",[])
            new_check_list =CheckList.objects.create(
                title=item["title"],

                date_to_start=date_to_start,
                time_to_start=time_to_start,
                date_to_end=date_to_end,
                time_to_end=time_to_end,
                responsible_for_doing=responsible_user,
                task=task,
                date_time_to_start_main = persian_to_gregorian(f"{date_to_start} {time_to_start}"),
                date_time_to_end_main = persian_to_gregorian(f"{date_to_end} {time_to_end}")

            )

            #
            for file_id in file_id_list:
                main_file = MainFile.objects.get(id=file_id)
                main_file.its_blong=True
                main_file.save()
                new_check_list.file.add(main_file)
            if item["difficulty"]:
                new_check_list.difficulty=item['difficulty']
            if item['label_id']:
                new_check_list.label_id=item['label_id']['id']
            new_check_list.save()
            create_reminde_a_task(chek_list=new_check_list)
        response_data = TaskSerializer(task).data
        success_notif =[]
        for member in task.check_list.all():

            if member.responsible_for_doing != request.user:
                if member.responsible_for_doing.id not in success_notif:

                    title = f"وظیفه جدید"
                    sub_title = f"وظیفه {task.title} توسط {request.user.fullname} به  پروژه شما اضافه شد"
                    create_notification(related_instance=task,workspace=WorkSpace.objects.get(id=workspace_id),user=member.responsible_for_doing,title=title,sub_title=sub_title,side_type="new_task")

                    success_notif.append(member.responsible_for_doing.id)
#

        short_text = task.title[:7] + "..."
        message = f"تسک {short_text} به بورد اضافه شد"
        create_notify_message(
            message=message,
            related_instance=task,
            project_id=task.project.id,
            creator_id=request.user.id
        )
        channel_layer = get_channel_layer()
        event ={
            "type":"send_one_task",
            "task_id":task.id
        }

        async_to_sync(channel_layer.group_send)(f"{project.id}_gp_project",event)
        return Response(status=status.HTTP_201_CREATED, data={"status": True, "message": "تسک جدید با موفقیت ثبت شد", "data": response_data})

    def put(self, request):
        """Update an existing task."""
        workspace_id = request.user.current_workspace_id
        request.data['workspace_id'] = workspace_id
        data = request.data

        task = get_object_or_404(Task, id=data.get("task_id"))

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
        success_notif = []
        for member in task.check_list.all():
            if member.responsible_for_doing.id not in success_notif:
                if member.responsible_for_doing != request.user:
                    title = f"بروزرسانی وظیفه"
                    sub_title = f"وظیفه {task.title} توسط {request.user.fullname} بروزرسانی شد"
                    create_notification(related_instance=task,workspace=workspace_obj,user=member.responsible_for_doing,title=title,sub_title=sub_title,side_type="update_task")
                    success_notif.append(member.responsible_for_doing.id)
        task.save()
        short_text = task.title[:7] + "..."
        message = f"تسک {short_text} بروزرسانی  شد"
        create_notify_message(
            message=message,
            related_instance=task,
            project_id=task.project.id,
            creator_id=request.user.id
        )
        channel_layer = get_channel_layer()
        event = {
            "type": "send_one_task",
            "task_id": task.id
        }

        async_to_sync(channel_layer.group_send)(f"{task.project.id}_gp_project",event)
        return Response(status=status.HTTP_202_ACCEPTED, data={"status": True, "message": "تسک با موفقیت آپدیت شد"})

    def delete(self, request):
        """Delete a task."""
        workspace_id = request.user.current_workspace_id
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        task = get_object_or_404(Task, id=request.data["task_id"])
        project_id = task.project.id
        short_text = task.title[:7] + "..."
        message = f"تسک {short_text}حذف شد "
        create_notify_message(
            message=message,
            related_instance=task,
            project_id=task.project.id,
            creator_id=request.user.id
        )
        task.delete()
        channel_layer = get_channel_layer()
        event ={
            "type":"send_event_task_list",
            "project_id":project_id
        }

        async_to_sync(channel_layer.group_send)(f"{project_id}_gp_project",event)

        return Response(status=status.HTTP_204_NO_CONTENT, data={"status": True, "message": "Task deleted"})





class CheckListManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]

    def _convert_jalali_to_datetime(self, date_str, time_str):
        """ Convert Jalali date and time string to a datetime object. """
        if date_str is None or time_str is None:
            return None  # Return None if date or time is missing

        try:
            year, month, day = map(int, date_str.split("/"))
            hour, minute = map(int, time_str.split(":"))
            return jdatetime.datetime(year, month, day, hour, minute).togregorian()
        except (ValueError, AttributeError):
            return None  # Return None if date or time format is invalid
    def get (self,request,checklist_id_or_task_id):
        check_list_obj = CheckList.objects.filter(task_id=checklist_id_or_task_id).order_by("date_time_to_start_main")
        check_list_serializer = CheckListSerializer(check_list_obj,many=True)



        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":check_list_serializer.data
        })
    def post(self,request,checklist_id_or_task_id):

        task_obj = get_object_or_404(Task,id=checklist_id_or_task_id)
        data = request.data

        label_id = data.get("label_id",None)
        title = data.get("title")

        responsible_for_doing = data.get("responsible_for_doing",None)
        date_to_start = data.get("date_to_start",None)
        time_to_start = data.get("time_to_start",None)
        file_id_list = data.get("file_id_list",[])
        date_to_end = data.get("date_to_end",None)
        time_to_end = data.get("time_to_end",None)

        check_list_obj = CheckList.objects.create(
            task=task_obj,
            title = title,
            date_to_start = date_to_start,
            time_to_start = time_to_start,
            date_to_end = date_to_end,
            time_to_end = time_to_end,
            date_time_to_start_main=persian_to_gregorian(f"{date_to_start} {time_to_start}"),
            date_time_to_end_main=persian_to_gregorian(f"{date_to_end} {time_to_end}")
        )
        if label_id and label_id != {}:
            check_list_obj.label_id=label_id['id']
        if responsible_for_doing:
            check_list_obj.responsible_for_doing_id=responsible_for_doing
        for file_id in file_id_list:
            main_file = MainFile.objects.get(id=file_id)
            main_file.its_blong = True
            main_file.save()
            check_list_obj.file.add(main_file)
        check_list_obj.save()
        short_text = check_list_obj.title[:7] + "..."
        task_short_text = check_list_obj.task.title[:7] + "..."
        message = f"چک لیست  {short_text}به تسک  {task_short_text} اضافه شد  "
        create_notify_message(
            message=message,
            related_instance=check_list_obj,
            project_id=check_list_obj.task.project.id,
            creator_id=request.user.id
        )
        channel_layer = get_channel_layer()
        event = {
            "type": "send_one_task",
            "task_id": task_obj.id
        }

        async_to_sync(channel_layer.group_send)(f"{task_obj.project.id}_gp_project",event)
        create_reminde_a_task(chek_list=check_list_obj)
        if request.user != check_list_obj.responsible_for_doing:
            title = f"بروزرسانی وظیفه"
            sub_title = f"چک لیست {check_list_obj.title} در تسک {check_list_obj.task.title} توسط {request.user.fullname} برای شما اضافه شد "
            create_notification(related_instance=check_list_obj.task,workspace=check_list_obj.task.project.workspace,user=check_list_obj.responsible_for_doing,title=title,sub_title=sub_title,side_type="update_task")
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

            if checklist_obj.responsible_for_doing == request.user:
                
                if data['status']:
                
                    checklist_obj.status=True
                else:
                    checklist_obj.status=False
                checklist_obj.save()
                channel_layer = get_channel_layer()
                event = {
                    "type": "send_one_task",
                    "task_id": checklist_obj.task.id
                }

                async_to_sync(channel_layer.group_send)(f"{checklist_obj.task.project.id}_gp_project", event)
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
            difficulty=data.get("difficulty",None)

            if label_id and label_id != {}:
                checklist_obj.label_id=label_id['id']
            if responsible_for_doing:
                checklist_obj.responsible_for_doing_id=responsible_for_doing
            
            checklist_obj.title =title
            checklist_obj.date_to_start =date_to_start
            checklist_obj.time_to_start =time_to_start
            checklist_obj.date_to_end =date_to_end
            checklist_obj.time_to_end =time_to_end
            try:
                checklist_obj.date_time_to_start_main = persian_to_gregorian(f"{date_to_start} {time_to_start}")
            except:
                pass

            try:
                checklist_obj.date_time_to_end_main = persian_to_gregorian(f"{date_to_end} {time_to_end}")
            except:
                pass




            checklist_obj.difficulty=difficulty
            existing_file_ids = list(checklist_obj.file.values_list("id", flat=True))

            # Update associated files
            file_ids = data.get("file_id_list", [])
            MainFile.objects.filter(id__in=file_ids).update(its_blong=True)
            checklist_obj.file.set(MainFile.objects.filter(id__in=file_ids))

            # Identify and delete files that are no longer associated with the task
            removed_file_ids = set(existing_file_ids) - set(file_ids)
            MainFile.objects.filter(id__in=removed_file_ids).delete()
            checklist_obj.save()
            channel_layer = get_channel_layer()
            event = {
                "type": "send_one_task",
                "task_id": checklist_obj.task.id
            }

            async_to_sync(channel_layer.group_send)(f"{checklist_obj.task.project.id}_gp_project", event)
            create_reminde_a_task(chek_list=checklist_obj)
            if request.user != checklist_obj.responsible_for_doing:
                title = f"بروزرسانی وظیفه"
                sub_title = f"چک لیست {checklist_obj.title} در تسک {checklist_obj.task.title} توسط {request.user.fullname} بروزرسانی شد "
                create_notification(related_instance=checklist_obj.task,
                                    workspace=checklist_obj.task.project.workspace,
                                    user=checklist_obj.responsible_for_doing, title=title, sub_title=sub_title,
                                    side_type="update_task")
            short_text = checklist_obj.title[:7] + "..."
            task_short_text = checklist_obj.task.title[:7] + "..."
            message = f"چک لیست  {short_text}در تسک  {task_short_text} بروزرسانی شد  "

            create_notify_message(
                message=message,
                related_instance=checklist_obj,
                project_id=checklist_obj.task.project.id,
                creator_id=request.user.id
            )
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":CheckListSerializer(checklist_obj).data
            })


    def delete(self,request,checklist_id_or_task_id):

        checklist_obj = get_object_or_404(CheckList,id=checklist_id_or_task_id)
        task_id = checklist_obj.task.id
        short_text = checklist_obj.title[:7] + "..."
        task_short_text = checklist_obj.task.title[:7] + "..."
        # message = f"چک لیست  {short_text}در تسک  {task_short_text} حذف شد  "
        #
        # create_notify_message(
        #     message=message,
        #     related_instance=checklist_obj,
        #     project_id=checklist_obj.project.id,
        #     creator_id=request.user.id
        # )
        checklist_obj.delete()
        channel_layer = get_channel_layer()

        event = {
            "type": "send_one_task",
            "task_id":task_id,
        }

        async_to_sync(channel_layer.group_send)(f"{checklist_obj.task.project.id}_gp_project", event)
        return Response(status=status.HTTP_204_NO_CONTENT)

        

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def get_project_users(request,project_id):
    workspace_id = request.user.current_workspace_id
    workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)

    project_obj = Project.objects.get(id=project_id)
    user_list = [
        {

            "fullname": workspace_obj.owner.fullname,
            "id": workspace_obj.owner.id,
            "avatar_url": workspace_obj.owner.avatar_url(),
            "self": request.user == workspace_obj.owner,
            "type":"owner",
            "permission":
                {
                    "permission_name": "project board",
                    "permission_type": "manager",
                },
        }
    ]
    for member in project_obj.members.all():
        if member != workspace_obj.owner :
            workspace_member = WorkspaceMember.all_objects.get(user_account=member, workspace=workspace_obj)
            dic={

                "fullname": workspace_member.fullname,
                "id": member.id,
                "avatar_url": member.avatar_url(),
                "self": request.user == member,
                "type":"member",
                "permission":{}
            }
            user_list.append(
                dic
            )


            try:
                for permission in workspace_member.permissions.all():
                    if permission.permission_name == "project board":
                        dic['permission'] =  {
                                "permission_name":permission.permission_name,
                                "permission_type":permission.permission_type
                            }


            except:
                dic['permission']={
                        "permission_name":"project board",
                        "permission_type":"no access",
                    }




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
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
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
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,report_id=None):
        data = request.data
        if report_id:
            report_obj = get_object_or_404(TaskReport,id=report_id)
            serializer_data = TaskReportSerializer(report_obj)
            serializer_data.data['self']=serializer_data.data['creator']['id'] == request.user.id
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        task_id = request.GET.get("task_id")
        task_obj = get_object_or_404(Task,id=task_id)
        report_objs = TaskReport.objects.filter(task=task_obj).order_by('-id')
        serializer_data = TaskReportSerializer(report_objs,many=True)
        for item in serializer_data.data:
            item['self'] = item['creator']['id'] == request.user.id

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
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
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

        department_objs= ProjectDepartment.objects.filter(workspace=workspace_obj)
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
    


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def my_task_checklist(request,project_id):
    page_number = request.GET.get("page_number",1)
    project_obj = get_object_or_404(Project,id=project_id)
    task_objs = Task.objects.filter(done_status=False,project=project_obj)

    check_list_objs = []
    for task in task_objs:
        for check_list in task.check_list.all().order_by("date_time_to_start_main"):
            if check_list.responsible_for_doing == request.user:
                check_list_objs.append(check_list)
    pagination_data = pagination(query_set=check_list_objs,page_number=page_number)


    if pagination_data['list'] != []:
        pagination_data['list'] = CheckListSerializer(pagination_data['list'],many=True).data


    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":pagination_data
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def referral_task(request,task_id):
    data =request.data
    project_id = data.get("project_id")
    task_obj = get_object_or_404(Task,id=task_id)
    project_obj = get_object_or_404(Project,id=project_id)
    first_category = CategoryProject.objects.filter(project=project_obj).first()
    task_obj.project =project_obj
    task_obj.category_task = first_category
    task_obj.save()
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"با موفقیت ارجاع داده شد",
        "data":{}
    })

class TaskArchiveManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]

    def get(self, request,task_id=None):
        if task_id:
            try:
                task_obj = Task.all_objects.get(id=task_id,is_deleted=True)
            except :
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer_data = TaskSerializer(task_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })

        page_number = request.GET.get("page_number", 1)
        project_id = request.GET.get("project_id")
        task_objs = Task.all_objects.filter(is_deleted=True,project_id=project_id)
        workspace_obj = get_object_or_404(WorkSpace, id=request.user.current_workspace_id)

        # ✅ If User is Workspace Owner
        if workspace_obj.owner == request.user:
            return self.get_paginated_response(task_objs, page_number)

        # ✅ Check if User is a Manager in Workspace
        workspace_member = WorkspaceMember.objects.filter(user_account=request.user, workspace=workspace_obj).first()
        if workspace_member and workspace_member.permissions.filter(permission_name="project board", permission_type="manager").exists():
            return self.get_paginated_response(task_objs, page_number)

        # ✅ If Not Owner or Manager, Filter Tasks Where User is Responsible
        task_filtered = [task for task in task_objs if any(check_list.responsible_for_doing == request.user for check_list in task.check_list.all())]

        return self.get_paginated_response(task_filtered, page_number)

    def get_paginated_response(self, queryset, page_number):
        pagination_data = pagination(query_set=queryset, page_number=page_number)
        pagination_data["list"] = TaskSerializer(pagination_data["list"], many=True).data if pagination_data["list"] else []

        return Response(
            status=status.HTTP_200_OK,
            data={"status": True, "message": "موفق", "data": pagination_data}
        )
    def put(self,request,task_id):
        try:
            task_obj = Task.all_objects.get(id=task_id, is_deleted=True)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        last_category_project = CategoryProject.objects.filter(project=task_obj.project).last()
        last_task = Task.objects.filter(project=task_obj.project,category_task=last_category_project).order_by("order").last()
        task_obj.order += last_task.order
        task_obj.is_deleted= False
        task_obj.save()
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"با موفقیت بازگردانی شد",
            "data":TaskSerializer(task_obj).data
        })
@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def check_list_archive(request,task_id):
    try:
        task_obj = Task.all_objects.get(id=task_id, is_deleted=True)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    check_list_objs = CheckList.all_objects.filter(task=task_obj)
    serializer_data = CheckListSerializer(check_list_objs,many=True)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"موفق",
        "data":serializer_data.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def completed_tasks(request):
    project_id = request.GET.get("project_id")
    page_number=request.GET.get("page_number",1)

    project_obj = get_object_or_404(Project,id=project_id)
    completed_task_objs= Task.objects.filter(project=project_obj,done_status=True)

    data = pagination(query_set=completed_task_objs,page_number=page_number)
    data['list'] = TaskSerializer(data['list'],many=True).data

    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"موفق",
        "data":data
    })





class MainTaskManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    channel_layer = get_channel_layer()

    def get(self,request,task_id=None):
        if task_id:
            task_obj = get_object_or_404(Task,id=task_id)
            serializer_data = TaskSerializer(task_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        project_id = request.GET.get("project_id")
        page_number = request.GET.get("page_number",1)
        task_objs = Task.objects.filter(project_id=project_id)

        paginate_data = pagination(query_set=task_objs,page_number=page_number)
        paginate_data['list'] = TaskSerializer(paginate_data['list'],many=True).data

        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "موفق",
            "data": paginate_data
        })
    def post(self,request):
        request.data['workspace_id'] = request.user.current_workspace_id
        workspace_id = request.user.current_workspace_id
        serializer_data = TaskSerializer(data=request.data,context={"user":request.user})
        if serializer_data.is_valid():
            task_obj = serializer_data.save()
            success_notif = []
            for member in task_obj.check_list.all():

                if member.responsible_for_doing != request.user:
                    if member.responsible_for_doing.id not in success_notif:
                        title = f"وظیفه جدید"
                        sub_title = f"وظیفه {task_obj.title} توسط {request.user.fullname} به  پروژه شما اضافه شد"
                        create_notification(related_instance=task_obj, workspace=WorkSpace.objects.get(id=workspace_id),
                                            user=member.responsible_for_doing, title=title, sub_title=sub_title,
                                            side_type="new_task")

                        success_notif.append(member.responsible_for_doing.id)


            short_text = task_obj.title[:7] + "..."
            message = f"تسک {short_text} به بورد اضافه شد"
            create_notify_message(
                message=message,
                related_instance=task_obj,
                project_id=task_obj.project.id,
                creator_id=request.user.id
            )

            event = {
                "type": "send_one_task",
                "task_id": task_obj.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{task_obj.project.id}_gp_project", event)
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت ثبت شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validations Error ",
            "data":serializer_data.errors
        })
    def put(self,request,task_id):
        request.data['workspace_id'] = request.user.current_workspace_id
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)


        task_obj= get_object_or_404(Task,id=task_id)
        request.data['project_id'] =  task_obj.project.id
        serializer_data= TaskSerializer(data=request.data,instance=task_obj,context={"user":request.user})
        if serializer_data.is_valid():
            task_obj = serializer_data.save()
            success_notif = []
            for member in task_obj.check_list.all():
                if member.responsible_for_doing.id not in success_notif:
                    if member.responsible_for_doing != request.user:
                        title = f"بروزرسانی وظیفه"
                        sub_title = f"وظیفه {task_obj.title} توسط {request.user.fullname} بروزرسانی شد"
                        create_notification(related_instance=task_obj, workspace=workspace_obj,
                                            user=member.responsible_for_doing, title=title, sub_title=sub_title,
                                            side_type="update_task")
                        success_notif.append(member.responsible_for_doing.id)
            task_obj.save()
            short_text = task_obj.title[:7] + "..."
            message = f"تسک {short_text} بروزرسانی  شد"
            create_notify_message(
                message=message,
                related_instance=task_obj,
                project_id=task_obj.project.id,
                creator_id=request.user.id
            )

            event = {
                "type": "send_one_task",
                "task_id": task_obj.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{task_obj.project.id}_gp_project", event)
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data

            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validations Error ",
            "data":serializer_data.errors
        })

    def delete (self,request,task_id):
        task = get_object_or_404(Task,id=task_id)
        project_id = task.project.id
        task.delete()
        event ={
            "type":"send_event_task_list",
            "project_id":project_id
        }

        async_to_sync(self.channel_layer.group_send)(f"{project_id}_gp_project",event)
        return Response(status=status.HTTP_204_NO_CONTENT)

class MainCheckListManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]

    channel_layer = get_channel_layer()
    def get(self,request,check_list_id=None):
        if check_list_id:
            check_list_obj = get_object_or_404(CheckList,id=check_list_id)
            serializer_data = CheckListSerializer(check_list_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        task_id = request.GET.get("task_id")
        page_number = request.GET.get("page_number",1)
        task_obj = get_object_or_404(Task,id=task_id)
        check_list_objs = CheckList.objects.filter(task=task_obj).order_by("-id")
        # pagination_data =pagination(query_set=check_list_objs,page_number=page_number,per_page_count=5)

        serializer_data = CheckListSerializer(check_list_objs,many=True)
        # pagination_data["list"]  = CheckListSerializer(pagination_data["list"],many=True).data
        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "موفق",
            "data": serializer_data.data
        })
    def post(self,request):
        request.data['workspace_id'] = request.user.current_workspace_id
        serializer_data = CheckListSerializer(data=request.data,context={"user":request.user})
        if serializer_data.is_valid():
            check_list_obj = serializer_data.save()
            short_text = check_list_obj.title[:7] + "..."
            task_short_text = check_list_obj.task.title[:7] + "..."
            message = f"چک لیست  {short_text}به تسک  {task_short_text} اضافه شد  "
            create_notify_message(
                message=message,
                related_instance=check_list_obj,
                project_id=check_list_obj.task.project.id,
                creator_id=request.user.id
            )

            event = {
                "type": "send_one_task",
                "task_id": check_list_obj.task.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{check_list_obj.task.project.id}_gp_project", event)
            create_reminde_a_task(chek_list=check_list_obj)
            if request.user != check_list_obj.responsible_for_doing:
                title = f"بروزرسانی وظیفه"
                sub_title = f"چک لیست {check_list_obj.title} در تسک {check_list_obj.task.title} توسط {request.user.fullname} برای شما اضافه شد "
                create_notification(related_instance=check_list_obj.task,
                                    workspace=check_list_obj.task.project.workspace,
                                    user=check_list_obj.responsible_for_doing, title=title, sub_title=sub_title,
                                    side_type="update_task")
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
    def put(self,request,check_list_id):
        instance = get_object_or_404(CheckList,id=check_list_id)
        request.data['workspace_id'] = request.user.current_workspace_id
        request.data['task_id'] = instance.task.id
        serializer_data = CheckListSerializer(instance=instance,data=request.data,context={"user":request.user})
        if serializer_data.is_valid():
            check_list_obj = serializer_data.save()

            event = {
                "type": "send_one_task",
                "task_id": check_list_obj.task.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{check_list_obj.task.project.id}_gp_project", event)
            create_reminde_a_task(chek_list=check_list_obj)
            if request.user != check_list_obj.responsible_for_doing:
                title = f"بروزرسانی وظیفه"
                sub_title = f"چک لیست {check_list_obj.title} در تسک {check_list_obj.task.title} توسط {request.user.fullname} بروزرسانی شد "
                create_notification(related_instance=check_list_obj.task,
                                    workspace=check_list_obj.task.project.workspace,
                                    user=check_list_obj.responsible_for_doing, title=title, sub_title=sub_title,
                                    side_type="update_task")
            short_text = check_list_obj.title[:7] + "..."
            task_short_text = check_list_obj.task.title[:7] + "..."
            message = f"چک لیست  {short_text}در تسک  {task_short_text} بروزرسانی شد  "

            create_notify_message(
                message=message,
                related_instance=check_list_obj,
                project_id=check_list_obj.task.project.id,
                creator_id=request.user.id
            )
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data
            })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "Validation Error",
            "data": serializer_data.errors

        })
    def delete (self,request,check_list_id):
        check_list_obj = get_object_or_404(CheckList,id=check_list_id)
        project_id= check_list_obj.task.project.id
        check_list_obj.delete()

        event ={
            "type":"send_event_task_list",
            "project_id":project_id
        }

        async_to_sync(self.channel_layer.group_send)(f"{project_id}_gp_project",event)
        return Response(status=status.HTTP_204_NO_CONTENT)



class CheckListTimerManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,timer_id):
        timer_obj = get_object_or_404(CheckListTimer,id=timer_id)
        serializer_data =CheckListTimerSerializer(timer_obj)
        # if check_list_obj.responsible_for_doing != request.user or check_list_obj.check_list_type != "based_on_weight":
        #     return Response(status=status.HTTP_400_BAD_REQUEST,data={
        #         "status":False,
        #         "message":"فقط کاربر "
        #     })
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":serializer_data.data
        })

    def post (self,request,timer_id):
        data= request.data
        command = data.get("command")
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
        timer_obj = get_object_or_404(CheckListTimer,id=timer_id)
        if command == "play":
            running_exists = CheckList.objects.filter(
                task__project__workspace=workspace_obj,
                responsible_for_doing=request.user,
                check_list_type="based_on_weight",
                timer__status="running"
            ).exists()

            if running_exists:
                return Response(
                    {
                        "status": False,
                        "message": "شما در حال حاضر تسک دیگری در حال اجرا دارید"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if timer_obj.status == "running":
                return Response(
                    {
                        "status":True,
                        "message":"این تسک در حال اجرا میباشد",
                        "data":CheckListTimerSerializer(timer_obj).data
                    },status=status.HTTP_201_CREATED
                )
            timer_obj.play()
            return Response(
                {
                    "status":True,
                    "message":"با موفقیت این تسک به اجرا درآمد",
                    "data": CheckListTimerSerializer(timer_obj).data
                },status=status.HTTP_201_CREATED
            )

        elif command == "pause":
            timer_obj.pause()
            return Response (
                {
                    "status": True,
                    "message": "با موفقیت این تسک متوقف شد",
                    "data": CheckListTimerSerializer(timer_obj).data
                },status=status.HTTP_201_CREATED
            )
        elif command == "stop":
            timer_obj.stop()
            return Response(
                {
                    "status": True,
                    "message": "با موفقیت این تسک پایان یافت",
                    "data": CheckListTimerSerializer(timer_obj).data
                },status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "status":False,
                    "message":"Invalid command"
                } ,status=status.HTTP_400_BAD_REQUEST
            )