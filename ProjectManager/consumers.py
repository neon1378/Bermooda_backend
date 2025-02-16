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

from .serializers import TaskSerializer,ProjectChatSerializer
import os
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
        paginator = Paginator(queryset.orderby("-id"), 20)  # Set items per page

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
            page = data.get("page",1)
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


class ProjectTask(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.user_type = self.scope['user_type']
        if self.user.is_authenticated:
            self.accept()
        else:
            self.close(code=1)
        self.project_id = self.scope['url_route']['kwargs']['project_id']

        self.project_obj = Project.objects.get(id=self.project_id)

        if self.user_type  == "member":
            for permission in self.scope['permissions']:
                if permission['permission_name'] == "project board":
                    self.permission = permission['permission_type']
        else:
            self.permission = "owner"
        async_to_sync(self.channel_layer.group_add)(
            f"{self.project_id}_amin",self.channel_name
        )
        if self.permission == "manager" or self.permission == "owner":
            task_objs = Task.objects.filter(project=self.project_obj,done_status=False)
        else:
            task_list = Task.objects.filter(project=self.project_obj, done_status=False)
            task_objs = [
                task
                for task in task_list
                if any(check_list.responsible_for_doing == self.user for check_list in task.check_list.all())
            ]


        serializer_data= TaskSerializer(task_objs,many=True)
        self.send(json.dumps(
            {
                "data_type":"task_list",
                "data":serializer_data.data
            }
        ))
    def receive(self, text_data=None, bytes_data=None):
        data= json.loads(text_data)
        command = data['command']

        if command == "get_task_list":
            if self.permission == "manager" or self.permission == "owner":
                task_objs = Task.objects.filter(project=self.project_obj, done_status=False)
            else:
                task_list = Task.objects.filter(project=self.project_obj, done_status=False)
                task_objs = [
                    task
                    for task in task_list
                    if any(check_list.responsible_for_doing == self.user for check_list in task.check_list.all())
                ]
            serializer_data= TaskSerializer(task_objs,many=True)
            self.send(json.dumps(
                {
                    "data_type":"task_list",
                    "data":serializer_data.data
                }
            ))
        elif command == "move_a_task":
            print (data)
            category_project_obj = get_object_or_404(CategoryProject,id=data['category_id'])
            task_obj = get_object_or_404(Task,id=data['task_id'])

            task_obj.category_task = category_project_obj
            task_obj.save()


            for order_task in data['orders_task']:
                task_obj = Task.objects.get(id=order_task['task_id'])
                task_obj.order = order_task['order']
                task_obj.save()
            
 
            event = {
                "type": "send_data",
                "category_id":data['category_id'],
                "task_id":data['task_id'],
            
                "orders_task":data['orders_task'],
                "project_id": self.project_id   
            }
        

            async_to_sync(self.channel_layer.group_send)(
               f"{self.project_id}_amin",event
                
            )
        elif command == "change_sub_task_status":
            
            task_id = data['task_id']
            sub_task_id = data['sub_task_id']
            status = data['status']
            
            sub_task_obj = get_object_or_404(CheckList,id=sub_task_id)
            if sub_task_obj.responsible_for_doing == self.user:
                sub_task_obj.status=status
                sub_task_obj.save()
                event = {
                    "type": "send_data",
                    "sub_task_id":data['sub_task_id'],
                    "task_id":task_id,
                
                    "status":data['status'],
                    "project_id": self.project_id   
                }
                async_to_sync(self.channel_layer.group_send)(
                    f"{self.project_id}_amin",event
                    
                )
            else:
                self.send(json.dumps({
                    "data_type":"error",
                    "message":"access denaid",
                    "data":{}
                }))

        elif command == "change_task_status":
            task_id = data['task_id']
            done_status = data['done_status']
            task_obj= get_object_or_404(Task,id=task_id)
            if self.user == self.project_obj.creator or self.project_obj.creator == None:
                task_obj.done_status=done_status
                task_obj.save()
                event = {
                    "type": "send_data",

                    "task_id":task_id,
                
                    "done_status":data['done_status'],
                    "project_id": self.project_id   
                }
                async_to_sync(self.channel_layer.group_send)(
                    f"{self.project_id}_amin",event
                    
                )
            else:
                self.send(json.dumps({
                    "data_type":"error",
                    "message":"access denaid",
                    "data":{}
                })) 
    def send_data(self,event):
        if self.permission == "manager" or self.permission == "owner":
            task_objs = Task.objects.filter(project=self.project_obj, done_status=False)
        else:
            task_list = Task.objects.filter(project=self.project_obj, done_status=False)
            task_objs = [
                task
                for task in task_list
                if any(check_list.responsible_for_doing == self.user for check_list in task.check_list.all())
            ]
        serializer_data = TaskSerializer(task_objs,many=True) 
        self.send(
            json.dumps(
                
                {
                    "data_type":"task_list",
                    "data":serializer_data.data

                }
            )
        )


    def disconnect(self,code=None):
        
         async_to_sync(self.channel_layer.group_discard)(
            self.project_id,
            self.channel_name
        )
         self.close(code=0)