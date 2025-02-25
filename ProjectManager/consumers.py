import json 
import django
django.setup()
from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from rest_framework.authtoken.models import Token
from UserManager.models import UserAccount
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from dotenv import load_dotenv
from WorkSpaceManager.models import  WorkspaceMember
from .serializers import TaskSerializer,ProjectChatSerializer
import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from .serializers import TaskSerializer
from core.models import MainFile
load_dotenv()



class ProjectChatWs(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']

        if self.user.is_authenticated:
            self.accept()
        else:
            self.close(code=1)
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_obj = Project.objects.get(id=self.project_id)
        async_to_sync(self.channel_layer.group_add)(
            f"{self.project_id}_chat",self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        base_url = os.getenv("BASE_URL")
        data = json.loads(text_data)

        if data['request_type'] == "create_message":
            message = data.get("message",None)

            

            new_project_chat = ProjectChat(creator=self.user,body=message,project=self.project_obj)
            try:
                voice_obj = MainFile.objects.get(id=data['voice'])
                new_project_chat.voice_file = voice_obj
                voice_obj.its_blong=True
                voice_obj.save()
            except:
                pass
            try:
                file_obj = MainFile.objects.get(id=data['file'])
                new_project_chat.main_file =file_obj
                file_obj.its_blong=True
                file_obj.save()
            except:pass
            # new_project_chat.project=new_project_chat
            new_project_chat.save()
            
            
            token = Token.objects.get_or_create(user=new_project_chat.creator)[0]
        
            event = {
                "type":"chat_handler",
                "message":message,
                "user_id":self.user.id,
                "new_project_chat_id":new_project_chat.id,
                "created":new_project_chat.jcreated()
                
            }
            
            async_to_sync(self.channel_layer.group_send)(
                f"{self.project_id}_chat",
                event
            )
        elif data['request_type'] == "read_message":

            messages = ProjectChat.objects.filter(project=self.project_obj).order_by("-id")
            message_list = []
            for message in messages:
                message_dic = {
                    "id":message.id,
                    "body":message.body,
                    "created":message.jcreated()
                    
                }
                if message.main_file:
                    message_dic['file'] = f"{base_url}{message.main_file.file.url}"
                if message.voice_file:
                    message_dic['voice'] = f"{base_url}{message.voice_file.file.url}"

                if message.creator.id == self.user.id:
                    message_dic['creator'] = "self"
                else:
                    message_dic['creator'] = "other"
                message_list.append(message_dic)
            self.send(json.dumps(
                message_list
            ))

    def chat_handler(self,event):
        base_url = os.getenv("BASE_URL")
        project_chat_obj = ProjectChat.objects.get(id=event['new_project_chat_id'])
        token = Token.objects.get_or_create(user=project_chat_obj.creator)[0]
        user_obj = UserAccount.objects.get(id=event['user_id'])
        message_data = {"message":{"body":event['message'], "created":event['created'],"fullname":user_obj.fullname}}
        if self.user.id == event['user_id'] :
            message_data['message']['creator'] = "self"
        else:
            message_data['message']['creator'] = "other"
        if project_chat_obj.main_file:
            message_data['message']['file'] = f"{base_url}{project_chat_obj.main_file.url}"
        if project_chat_obj.voice_file:
            message_data['message']['voice']  = f"{base_url}{project_chat_obj.voice_file.url}"
        self.send(json.dumps(
            message_data
        ))

    def disconnect(self,code=None):
        
        async_to_sync(self.channel_layer.group_discard)(
            f"{self.project_id}_chat",
            self.channel_name
        )
        self.close(code=0)



class ProjectChatMainWs(WebsocketConsumer):
    def paginate_queryset(self,page_number,queryset):


        # Set up custom pagination
        paginator = Paginator(queryset.order_by("-id"), 20)  # Set items per page

        # Check if the requested page exists
        if page_number > paginator.num_pages:
            return {
                "count": paginator.count,
                "next": None,
                "previous": None,
                "data": []
            }

        # Get the page
        page = paginator.get_page(page_number)
        serializer_data=ProjectChatSerializer(page.object_list,many=True)
        for item in serializer_data.data:
            item['creator']['self'] = item['creator']['id'] == self.user.id
        return {
            "count": paginator.count,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": serializer_data.data
        }

    def connect(self):
        self.user = self.scope['user']

        if self.user.is_authenticated:
            self.accept()
        else:
            self.close(code=1)
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_obj = Project.objects.get(id=self.project_id)
        async_to_sync(self.channel_layer.group_add)(
            f"{self.project_id}_main",self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        base_url = os.getenv("BASE_URL")
        data = json.loads(text_data)

        if data['command'] == "create_message":
            data['data']['creator_id'] = self.user.id
            data['data']['project_id'] = self.project_obj.id

            

            serializer_data = ProjectChatSerializer(data=data['data'])
            if serializer_data.is_valid():
                new_project_chat = serializer_data.save()


          
            
          
        
                event = {
                    "type":"chat_handler",
                    "chat_id":new_project_chat.id,
                    "creator_id" :self.user.id
                   
                

                    
                }
                async_to_sync(self.channel_layer.group_send)(
                    f"{self.project_id}_main",
                    event
                )
            else:
                self.send(json.dumps(
                    serializer_data.errors
                ))
         
        elif data['command'] == "message_list":
            try:
                page = data['data']['page']
            except:
                page = 1
            project_chats = ProjectChat.objects.filter(project=self.project_obj).order_by("-id")
            data = self.paginate_queryset(page_number=page,queryset=project_chats)

            self.send(json.dumps(
                {
                    "data_type":"message_list",
                    "data":data
                }
            ))

    def chat_handler(self,event):
        project_chat_obj = ProjectChat.objects.get(id=event['chat_id'])

        serializer_data= ProjectChatSerializer(project_chat_obj)
        serializer_data.data['creator']['self'] = serializer_data.data['creator']['id'] == self.user.id
        self.send(json.dumps(
            {
                "data_type":"create_message",
                "data":serializer_data.data,


            }
        ))

    def disconnect(self,code=None):
        
        async_to_sync(self.channel_layer.group_discard)(
            f"{self.project_id}_main",
            self.channel_name
        )
        self.close(code=0)





class ProjectTaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.project_id = self.scope['url_route']['kwargs']['project_id']

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        await self.accept()

        try:
            self.project_obj = await self.get_project(self.project_id)
            self.workspace_obj = self.project_obj.workspace
        except ObjectDoesNotExist:
            await self.close(code=4004)
            return

        await self.channel_layer.group_add(
            f"project_{self.project_id}_admin",
            self.channel_name
        )

        await self.send_task_list()

    @database_sync_to_async
    def get_project(self, project_id):
        return Project.objects.select_related('workspace').get(id=project_id)

    async def send_task_list(self):
        task_objs = await self.get_filtered_tasks()
        serializer_data = await self.serialize_tasks(task_objs)
        await self.send_json({
            "data_type": "task_list",
            "data": serializer_data
        })

    @database_sync_to_async
    def get_filtered_tasks(self):
        base_qs = Task.objects.filter(
            project=self.project_obj,
            done_status=False
        ).prefetch_related('check_list')

        if self.is_admin_or_manager():
            return list(base_qs)
        return list(base_qs.filter(check_list__responsible_for_doing=self.user).distinct())

    @database_sync_to_async
    def is_admin_or_manager(self):
        return (
                self.workspace_obj.owner == self.user or
                self.get_permission_type() == "manager"
        )

    @database_sync_to_async
    def get_permission_type(self):
        try:
            member = WorkspaceMember.objects.get(
                user_account=self.user,
                workspace=self.workspace_obj
            )
            perm = member.permissions.filter(
                permission_name="project board"
            ).first()
            return perm.permission_type if perm else None
        except ObjectDoesNotExist:
            return None

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            command = data['command']

            handler = getattr(self, f'handle_{command}', None)
            if handler:
                await handler(data)
            else:
                await self.send_error("Invalid command")
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")

    async def handle_task_list(self, data):
        await self.send_task_list()

    async def handle_move_a_task(self, data):
        task_obj = await self.get_task(data['task_id'])
        category = await self.get_category(data['category_id'])

        await self.update_task_category(task_obj, category)
        await self.update_task_orders(data['orders_task'])

        await self.broadcast_event({
            "type": "task_moved",
            "category_id": data['category_id'],
            "task_id": data['task_id'],
            "orders_task": data['orders_task']
        })

    async def handle_change_sub_task_status(self, data):
        sub_task = await self.get_sub_task(data['sub_task_id'])
        if not await self.validate_sub_task_owner(sub_task):
            await self.send_error("Access denied")
            return

        await self.update_sub_task_status(sub_task, data['status'])
        await self.broadcast_event({
            "type": "subtask_updated",
            "task_id": data['task_id'],
            "sub_task_id": data['sub_task_id'],
            "status": data['status']
        })

    async def handle_change_task_status(self, data):
        task = await self.get_task(data['task_id'])
        if not await self.validate_task_owner(task):
            await self.send_error("Access denied")
            return

        await self.update_task_status(task, data['done_status'])
        await self.broadcast_event({
            "type": "task_status_changed",
            "task_id": data['task_id'],
            "done_status": data['done_status']
        })

    # Database operations
    @database_sync_to_async
    def get_task(self, task_id):
        return get_object_or_404(Task, id=task_id)

    @database_sync_to_async
    def get_category(self, category_id):
        return get_object_or_404(CategoryProject, id=category_id)

    @database_sync_to_async
    def update_task_category(self, task, category):
        task.category_task = category
        task.save()

    @database_sync_to_async
    def update_task_orders(self, orders):
        tasks = Task.objects.filter(id__in=[o['task_id'] for o in orders])
        task_map = {t.id: t for t in tasks}
        for order in orders:
            if task := task_map.get(order['task_id']):
                task.order = order['order']
        Task.objects.bulk_update(tasks, ['order'])

    @database_sync_to_async
    def get_sub_task(self, sub_task_id):
        return get_object_or_404(CheckList, id=sub_task_id)

    @database_sync_to_async
    def validate_sub_task_owner(self, sub_task):
        return sub_task.responsible_for_doing == self.user

    @database_sync_to_async
    def update_sub_task_status(self, sub_task, status):
        sub_task.status = status
        sub_task.save()

    @database_sync_to_async
    def validate_task_owner(self, task):
        return task.project.creator in [self.user, None]

    @database_sync_to_async
    def update_task_status(self, task, status):
        task.done_status = status
        task.save()

    @database_sync_to_async
    def serialize_tasks(self, tasks):
        return TaskSerializer(tasks, many=True).data

    # Helpers
    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))

    async def send_error(self, message):
        await self.send_json({
            "data_type": "error",
            "message": message,
            "data": {}
        })

    async def broadcast_event(self, event):
        event["project_id"] = self.project_id
        await self.channel_layer.group_send(
            f"project_{self.project_id}_admin",
            event
        )

    async def task_moved(self, event):
        await self.send_task_list()

    async def subtask_updated(self, event):
        await self.send_task_list()

    async def task_status_changed(self, event):
        await self.send_task_list()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"project_{self.project_id}_admin",
            self.channel_name
        )
        await self.close(close_code)

# class ProjectTask(WebsocketConsumer):
#     def connect(self):
#         self.user = self.scope['user']
#
#         if self.user.is_authenticated:
#             self.accept()
#
#         else:
#             self.close(code=1)
#         self.project_id = self.scope['url_route']['kwargs']['project_id']
#
#         self.project_obj = Project.objects.get(id=self.project_id)
#         self.workspace_obj = self.project_obj.workspace
#         if self.workspace_obj.owner == self.user or self.get_permission_user() == "manager":
#             task_objs = Task.objects.filter(project=self.project_obj, done_status=False)
#         else:
#             task_list = Task.objects.filter(project=self.project_obj, done_status=False)
#             task_objs = [
#                 task
#                 for task in task_list
#                 if any(check_list.responsible_for_doing == self.user for check_list in task.check_list.all())
#             ]
#         serializer_data = TaskSerializer(task_objs, many=True)
#         self.send(
#             json.dumps(
#
#                 {
#                     "data_type": "task_list",
#                     "data": serializer_data.data
#
#                 }
#             )
#         )
#         async_to_sync(self.channel_layer.group_add)(
#             f"{self.project_id}_amin",self.channel_name
#         )
#
#     def get_permission_user(self):
#         workspace_member = WorkspaceMember.objects.get(user_account=self.user, workspace=self.workspace_obj)
#         for permission in workspace_member.permissions.all():
#             if permission.permission_name == "project board":
#                 return permission.permission_type
#     def receive(self, text_data=None, bytes_data=None):
#         data= json.loads(text_data)
#         command = data['command']
#
#         if command == "task_list":
#
#             if self.workspace_obj.owner == self.user or self.get_permission_user() == "manager":
#                 task_objs = Task.objects.filter(project=self.project_obj, done_status=False)
#             else:
#                 task_list = Task.objects.filter(project=self.project_obj, done_status=False)
#                 task_objs = [
#                     task
#                     for task in task_list
#                     if any(check_list.responsible_for_doing == self.user for check_list in task.check_list.all())
#                 ]
#             serializer_data= TaskSerializer(task_objs,many=True)
#             self.send(json.dumps(
#                 {
#                     "data_type":"task_list",
#                     "data":serializer_data.data
#                 }
#             ))
#         elif command == "move_a_task":
#
#             category_project_obj = get_object_or_404(CategoryProject,id=data['category_id'])
#             task_obj = get_object_or_404(Task,id=data['task_id'])
#
#             task_obj.category_task = category_project_obj
#             task_obj.save()
#
#
#             for order_task in data['orders_task']:
#                 task_obj = Task.objects.get(id=order_task['task_id'])
#                 task_obj.order = order_task['order']
#                 task_obj.save()
#
#
#             event = {
#                 "type": "send_data",
#                 "category_id":data['category_id'],
#                 "task_id":data['task_id'],
#
#                 "orders_task":data['orders_task'],
#                 "project_id": self.project_id
#             }
#
#
#             async_to_sync(self.channel_layer.group_send)(
#                f"{self.project_id}_amin",event
#
#             )
#         elif command == "change_sub_task_status":
#
#             task_id = data['task_id']
#             sub_task_id = data['sub_task_id']
#             status = data['status']
#
#             sub_task_obj = get_object_or_404(CheckList,id=sub_task_id)
#             if sub_task_obj.responsible_for_doing == self.user:
#                 sub_task_obj.status=status
#                 sub_task_obj.save()
#                 event = {
#                     "type": "send_data",
#                     "sub_task_id":data['sub_task_id'],
#                     "task_id":task_id,
#
#                     "status":data['status'],
#                     "project_id": self.project_id
#                 }
#                 async_to_sync(self.channel_layer.group_send)(
#                     f"{self.project_id}_amin",event
#
#                 )
#             else:
#                 self.send(json.dumps({
#                     "data_type":"error",
#                     "message":"access denaid",
#                     "data":{}
#                 }))
#
#         elif command == "change_task_status":
#             task_id = data['task_id']
#             done_status = data['done_status']
#             task_obj= get_object_or_404(Task,id=task_id)
#             if self.user == self.project_obj.creator or self.project_obj.creator == None:
#                 task_obj.done_status=done_status
#                 task_obj.save()
#                 event = {
#                     "type": "send_data",
#
#                     "task_id":task_id,
#
#                     "done_status":data['done_status'],
#                     "project_id": self.project_id
#                 }
#                 async_to_sync(self.channel_layer.group_send)(
#                     f"{self.project_id}_amin",event
#
#                 )
#             else:
#                 self.send(json.dumps({
#                     "data_type":"error",
#                     "message":"access denaid",
#                     "data":{}
#                 }))
#     def send_data(self,event):
#         if self.workspace_obj.owner == self.user or self.get_permission_user() == "manager":
#             task_objs = Task.objects.filter(project=self.project_obj, done_status=False)
#         else:
#             task_list = Task.objects.filter(project=self.project_obj, done_status=False)
#             task_objs = [
#                 task
#                 for task in task_list
#                 if any(check_list.responsible_for_doing == self.user for check_list in task.check_list.all())
#             ]
#         serializer_data = TaskSerializer(task_objs,many=True)
#         self.send(
#             json.dumps(
#
#                 {
#                     "data_type":"task_list",
#                     "data":serializer_data.data
#
#                 }
#             )
#         )
#
#
#     def disconnect(self,code=None):
#
#          async_to_sync(self.channel_layer.group_discard)(
#             self.project_id,
#             self.channel_name
#         )
#          self.close(code=0)