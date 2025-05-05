import json 
import django
django.setup()
from django.db.models import Prefetch
from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from core.widgets import pagination
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from rest_framework.authtoken.models import Token
from UserManager.models import UserAccount
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from dotenv import load_dotenv
from WorkSpaceManager.models import  WorkspaceMember
from .serializers import TaskSerializer,ProjectChatSerializer,ProjectMessageSerializer
import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


from core.models import MainFile
load_dotenv()








class ProjectTask(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.project_id = self.scope['url_route']['kwargs']['project_id']

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        try:
            # Use sync_to_async for database operations
            self.project_obj = await sync_to_async(Project.objects.get)(id=self.project_id)
            self.workspace_obj = await sync_to_async(lambda: self.project_obj.workspace)()
        except ObjectDoesNotExist:
            await self.close(code=4004)
            return

        await self.accept()

        # Send initial data
        await self.send_initial_data()

        # Add to channel group
        await self.channel_layer.group_add(
            f"{self.project_id}_admin",
            self.channel_name
        )


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"{self.project_id}_admin",
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            print(data,"!@#!@#")
            command = data.get('command')

            command_handlers = {
                'task_list': self.handle_task_list,
                'move_a_task': self.handle_move_task,
                'change_sub_task_status': self.handle_subtask_status,
                'change_task_status': self.handle_task_status,
                "read_all_messages":self.read_all_messages,
                "create_a_message":self.create_a_message,
                "edit_message":self.edit_message,
            }

            handler = command_handlers.get(command)
            if handler:
                await handler(data)
            else:
                await self.send_error("Invalid command")

        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            await self.send_error(str(e))

    async def send_initial_data(self):
        """Send initial task list data on connection"""
        task_data = await self._main_serializer_data()
        message_data = await self._all_message_serializer(page_number=1)
        await self.send_json({
            "data_type": "task_list",
            "data": task_data
        })
        await self.send_json({
            "data_type": "all_messages",
            "data": message_data
        })
    @sync_to_async
    def _one_task_serializer(self,task_id):
        task_obj = Task.objects.get(id=task_id)
        task_data = {
            "category_id": task_obj.category_task.id,
            "color": task_obj.category_task.color_code,
            "title": task_obj.category_task.title,
            "task_data": TaskSerializer(task_obj).data
        }
        return  task_data

    async def send_one_task(self, event):


        task_data = await self._one_task_serializer(task_id=event['task_id'])

        await self.send_json({
            "data_type": "get_a_task",
            "data": task_data
        })

    @sync_to_async
    def _one_message_serializer(self,message_id):
        message_obj = get_object_or_404(ProjectMessage,id=message_id)
        serializer_data = ProjectMessageSerializer(message_obj,context={"user":self.user})
        return serializer_data.data

    @sync_to_async
    def _all_message_serializer(self,page_number,per_page_count=None):

        message_objs = ProjectMessage.objects.filter(project=self.project_obj).order_by("-id")
        if per_page_count:
            pagination_data = pagination(query_set=message_objs,page_number=page_number,per_page_count=per_page_count)
        else:
            pagination_data = pagination(query_set=message_objs,page_number=page_number)


        pagination_data['current_page'] = page_number
        pagination_data['list'] = ProjectMessageSerializer(pagination_data['list'],many=True,context={"user":self.user}).data

        return pagination_data

    @sync_to_async
    def _edit_a_message(self,data):
        main_data= data['data']
        message_obj = get_object_or_404(ProjectMessage,id=main_data['message_id'])
        message_obj.body = main_data['body']
        message_obj.save()
        return {
            "status":True,
            "data":{
                "message_id":message_obj.id
            }
        }
    async def edit_message(self,data):
        message_data = await self._edit_a_message(data=data)

        await self.broadcast_event({
            "type": "send_a_message",
            "message_id": message_data['data']['message_id']

        })


    @sync_to_async
    def _create_a_message(self,data):
        main_data = data['data']
        main_data['project_id'] = self.project_obj.id
        main_data['creator_id'] = self.user.id
        serializer_data =ProjectMessageSerializer(data=main_data,context={"user":self.user})
        if serializer_data.is_valid():
            message_obj = serializer_data.save()
            return {
                "status":True,
                "data":{
                    "message_id":message_obj.id
                }
            }

        return {
            "status":False,
            "data":serializer_data.errors
        }
    async def read_all_messages(self,data):
        try:
            main_data = data.get("data",None)
            page_number= main_data.get("page_number",1)
            per_page_count = main_data.get("per_page_count",None)
        except:
            per_page_count = None
            page_number = 1

        message_data = await self._all_message_serializer(page_number=page_number,per_page_count=per_page_count)
        await self.send(json.dumps({
            "data_type":"all_messages",
            "data":message_data
        }))
    async def create_a_message(self,data):
        message_data = await self._create_a_message(data=data)
        if message_data['status']:
            await self.broadcast_event({
                "type": "send_a_message",
                "message_id": message_data['data']['message_id']

            })
        else:
            await self.send(json.dumps({
                "data_type":"Validation Error",
                "data":message_data['data']
            }))

    async def send_a_message(self,event):

        message_data = await self._one_message_serializer(message_id=event['message_id'])
        await self.send(json.dumps({
            "data_type":"send_a_message",
            "data":message_data

        }))





    @sync_to_async
    def _main_serializer_data(self):
        """Generate structured task data with categories more efficiently."""
        # Fetch all categories in a single query
        category_objs = CategoryProject.objects.filter(project=self.project_obj).order_by("-id")
        all_categories = {cat.id: cat for cat in category_objs}

        # Get tasks with optimized related data fetching
        task_objs = self._get_filtered_tasks()

        # Serialize tasks, leveraging pre-fetched related data
        serializer_data = TaskSerializer(task_objs, many=True).data

        # Organize tasks by category using serializer data
        categories = {}
        for task in serializer_data:
            category_id = task['category_task_id']
            if category_id not in all_categories:
                continue  # Skip invalid categories (data integrity issue)

            # Use category data from serializer to maintain compatibility
            category_data = task["category_task"]
            if category_id not in categories:
                categories[category_id] = {
                    "category_id": category_id,
                    "project_id":self.project_obj.id,
                    "color": category_data['color_code'],
                    "title": category_data['title'],
                    "task_list": []
                }
            categories[category_id]['task_list'].append(task)

        # Fill in empty categories from pre-fetched data
        for category in category_objs:
            if category.id not in categories:
                categories[category.id] = {
                    "category_id": category.id,
                    "color": category.color_code,
                    "project_id":self.project_obj,
                    "title": category.title,
                    "task_list": []
                }

        # Return sorted results
        return sorted(categories.values(), key=lambda x: x['category_id'])

    def _get_filtered_tasks(self):
        """Optimized task fetching with smart prefetching."""
        base_qs = Task.objects.filter(
            project=self.project_obj,
            done_status=False
        ).select_related('category_task').prefetch_related(
            Prefetch('check_list',
                     queryset=CheckList.objects.select_related('responsible_for_doing'))
        )
        print(self._has_admin_access())
        if self._has_admin_access():
            return base_qs
        task_list = []
        for task in base_qs:
            for check_list in task.check_list.all():
                if check_list.responsible_for_doing == self.user:
                    task_list.append(task)
                    break
        return task_list
        # return [task for task in base_qs
        #         if any(check.responsible_for_doing == self.user
        #                for check in task.check_list.all())]
    @sync_to_async
    def _has_admin_access(self):

        """Check if user has admin-level permissions"""
        return (
                self.workspace_obj.owner == self.user or
                self._get_permission_type() == "manager"
        )

    @sync_to_async
    def _get_permission_type(self):
        """Get user's permission type for the workspace"""
        try:
            member = WorkspaceMember.objects.get(
                user_account=self.user,
                workspace=self.workspace_obj
            )
            for permission in member.permissions.all():
                if permission.permission_name == "project board":
                    return  permission.permission_type

        except ObjectDoesNotExist:
            return None

    async def handle_task_list(self, data):
        """Handle task list refresh requests"""
        data = await self._main_serializer_data()
        await self.send_json({
            "data_type": "task_list",
            "data": data
        })

    async def handle_move_task(self, data):
        """Handle task movement between categories"""
        category = await sync_to_async(get_object_or_404)(
            CategoryProject,
            id=data['category_id']
        )
        task = await sync_to_async(get_object_or_404)(Task, id=data['task_id'])

        # Update task category
        task.category_task = category
        await sync_to_async(task.save)()

        # Update task orders
        for order_data in data['orders_task']:
            t = await sync_to_async(Task.objects.get)(id=order_data['task_id'])
            t.order = order_data['order']
            await sync_to_async(t.save)()

        # Broadcast update

        await self.broadcast_event({
            "type": "send_one_task",
            "task_id": data['task_id']
        })


    async def handle_subtask_status(self, data):
        """Handle subtask status changes"""

        # Fetch subtask synchronously
        subtask = await sync_to_async(
            lambda: CheckList.objects.select_related("responsible_for_doing").get(id=data['sub_task_id']),
            thread_sensitive=True)()

        # Fetch user synchronously
        responsible_user = await sync_to_async(lambda: subtask.responsible_for_doing, thread_sensitive=True)()
        task_obj = await  sync_to_async(lambda: subtask.task, thread_sensitive=True)()
        if responsible_user != self.user:
            raise PermissionDenied("Access denied")

        # Update status
        subtask.status = data['status']
        await sync_to_async(subtask.save, thread_sensitive=True)()


        # Broadcast the event
        await self.broadcast_event({
            "type": "send_one_task",
            "task_id": task_obj.id
        })

    async def handle_task_status(self, data):
        """Handle main task status changes"""
        task = await sync_to_async(get_object_or_404)(Task, id=data['task_id'])

        if not self._has_admin_access():
            raise PermissionDenied("Access denied")

        task.done_status = data['done_status']
        await sync_to_async(task.save)()


        await self.broadcast_event({
            "type": "send_data",
            **data,
            "project_id": self.project_id
        })

    async def broadcast_event(self, event):
        """Helper method for broadcasting events to group"""
        await self.channel_layer.group_send(
            f"{self.project_id}_admin",
            event
        )

    async def send_data(self, event):
        """Handler for group send events"""
        await self.send_json({
            "data_type": "task_list",
            "data": await self._main_serializer_data()
        })

    async def send_json(self, data):
        """Helper method for sending JSON data"""
        await self.send(text_data=json.dumps(data))

    async def send_error(self, message):
        """Helper method for sending error messages"""
        await self.send_json({
            "data_type": "error",
            "message": message,
            "data": {}
        })