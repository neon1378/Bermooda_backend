import json 
import django
django.setup()
from django.db.models import Prefetch
from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

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
            command = data.get('command')

            command_handlers = {
                'task_list': self.handle_task_list,
                'move_a_task': self.handle_move_task,
                'change_sub_task_status': self.handle_subtask_status,
                'change_task_status': self.handle_task_status,
                "read_all_messages":self.read_all_messages,
                "create_a_message":self.create_a_message,
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
        data = await self._main_serializer_data()
        await self.send_json({
            "data_type": "task_list",
            "data": data
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
    def _all_message_serializer(self):
        message_objs = ProjectMessage.objects.filter(project=self.project_obj).order_by("-id")
        serializer_data = ProjectMessageSerializer(message_objs,many=True,context={"user":self.user})
        return serializer_data.data



    @sync_to_async
    def _create_a_message(self,data):
        main_data = data['data']
        main_data['project_id'] = self.project_obj.id
        main_data['creator_id'] = self.user.id
        serializer_data =ProjectMessageSerializer(data=main_data)
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
        message_data = await self._all_message_serializer()
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

        if self._has_admin_access():
            return base_qs
        return [task for task in base_qs
                if any(check.responsible_for_doing == self.user
                       for check in task.check_list.all())]
    @sync_to_async
    def _has_admin_access(self):
        print(self._get_permission_type()  == "manager","!@#!@#!@#")
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
            # return next(
            #     (p.permission_type for p in member.permissions.all()
            #      if p.permission_name == "project board"),
            #     None
            # )
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