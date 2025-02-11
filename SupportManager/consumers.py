import json 
from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
import urllib.parse
from django.utils.timezone import make_aware, is_aware
from WorkSpaceManager.models import WorkSpace
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from channels.layers import get_channel_layer
from datetime import datetime

class ChatMessageWs(WebsocketConsumer):
    def connect(self):  
   
        self.user= self.scope['user']
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = urllib.parse.parse_qs(query_string)
        self.anon_user_phone = query_params.get('phone_number', [None])[0]
        self.anon_user_fullname = query_params.get('fullname', [None])[0]



        if self.user.is_authenticated:
            self.side_type = "manager"
            self.phone = self.user.phone_number
            async_to_sync(self.channel_layer.group_add)(
                f"{self.user.id}_user",
                self.channel_name
            )
        elif self.anon_user_phone:
            try :
                self.anon_user = AnonCustomer.objects.get(phone_number=self.anon_user_phone)
            except :
                self.anon_user = AnonCustomer(
                    phone_number = self.anon_user_phone,
                    fullname=self.anon_user_fullname
                )
                self.anon_user.save()
            self.side_type = "client"

            async_to_sync(self.channel_layer.group_add)(
                f"{self.anon_user.id}_anon_user",
                self.channel_name
            )
        else:
            self.close(code=0)
        self.accept()


    def make_workspace_room(self,group_room_obj):
                    group_dic = {
                        "group_id": group_room_obj.id,
                        "brand_name": group_room_obj.workspace.jadoo_brand_name,
                        "avatar_url":group_room_obj.workspace.avatar_url(),
                        "last_message": "",
                        "unread_message": 0,
                        "last_department": "",
                        "room_list": []
                    }

                    room_objs = Room.objects.filter(group=group_room_obj)
                    last_messages = []
                    room_list = []
                    
                    department_objs= Department.objects.filter(workspace = group_room_obj.workspace)
                 
                    for department_obj in department_objs:
                        department_exists= False
                        for room_obj in room_objs:
                            if room_obj.department == department_obj:
                                department_exists=True
                                unread_messages_count = room_obj.messages.filter(message_type="operator", read_status=False).count()
                                group_dic['unread_message'] += unread_messages_count

                                last_message = room_obj.messages.last()
                                last_message_text = last_message.body if last_message else ""

                                room_dic = {
                                    "room_id": room_obj.id,
                                    "brand_name": room_obj.workspace.jadoo_brand_name,
                            
                                    "department_id": room_obj.department.id,
                                    "title": room_obj.department.title,
                                    "color_code": room_obj.department.color_code,
                        
                            
                                    "last_message_text": last_message_text,
                                    "unread_message": unread_messages_count,
                                    "last_message_date_time":last_message.jtime() if last_message else None,

                                }

                                if last_message and last_message.created:
                                    last_messages.append(last_message)

                                room_list.append(room_dic)
                        if not department_exists:
                         
                            new_room_obj = Room(
                                workspace = department_obj.workspace,
                                department= department_obj,
                                group=group_room_obj,
                                anon_customer =self.anon_user,
                                room_status="waiting",

                            )
                            new_room_obj.save()

                            room_dic = {
                                    "room_id": new_room_obj.id,
                                    "brand_name": new_room_obj.workspace.jadoo_brand_name,
                            
                                    "department_id": new_room_obj.department.id,
                                    "title": new_room_obj.department.title,
                                    "color_code": new_room_obj.department.color_code,
                        
                            
                                    "last_message_text": "",
                                    "unread_message": 0,
                            }
                    # Sort last_messages by created date, handling None values

                    last_messages.sort(key=lambda msg: msg.created or datetime.min)
                  
                    group_dic['room_list'] = room_list
                    group_dic['last_message'] = last_messages[-1].body if last_messages else ""
                    group_dic['last_department'] = last_messages[-1].room.department.title if last_messages else ""
                    group_dic['last_message_obj'] = last_messages[-1] if last_messages else None
                    return group_dic
                    
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        command = data['command']
        if self.side_type == "client":
           
            if command == "read workspaces":
                self.group_room_objs = GroupRoom.objects.filter(anon_customer=self.anon_user, status=True)
                group_data = []

                for group_room_obj in self.group_room_objs:
                    group_data.append(self.make_workspace_room(group_room_obj=group_room_obj))
                
                def get_sort_key(msg):
                    created = msg['last_message_obj'].created if msg['last_message_obj'] else datetime.min
                    return make_aware(created) if not is_aware(created) else created

                group_data.sort(key=get_sort_key, reverse=True)
                                

                for item in group_data:
                    try:
                        item['last_message_date_time'] = item['last_message_obj'].jtime()
                        del item['last_message_obj']
                    except:
                        del item['last_message_obj']
        
                self.send(json.dumps({
                        "data_type":"group list",
                        "data":group_data
                    }))
    
            elif command == "read room message":
                
                page = data.get("page",1)
   
                self.room_messages = self.room_obj.messages.filter(message_type="operator",read_status=False)
                for room_message in self.room_messages:
                    room_message.read_status=True
                    room_message.save()
                message_data =self.paginate_queryset(page,self.room_obj)
                self.send(json.dumps(
                    {
                        "data_type":"room messages",
                        "data":message_data
                        
                    }
                ))
            
            
            # open and close room_id group
            elif command == "open room message":
                self.room_id = data['room_id']
                self.room_obj = get_object_or_404(Room,id=self.room_id)
                async_to_sync(self.channel_layer.group_add)(
                    str(self.room_id),
                    self.channel_name
                )
            elif command == "close room message":
                async_to_sync(self.channel_layer.group_discard)(
                    str(self.room_id),
                    self.channel_name
                )
            elif command == "create new message":

                text = data.get("text",None)
                file_id= data.get("file_id",None)
                voice_id= data.get("voice_id",None)
                image_id= data.get("image_id",None)

                self.new_room_message = RoomMessage(
                    message_type = 'anonymous',
                    room = self.room_obj,
                    body = text,

                )
                message_data =""
                if file_id:
                    self.new_room_message.file_id=file_id
                    message_data = "file"
                if voice_id:
                    self.new_room_message.voice_id=voice_id
                    message_data = "voice"
                
                if image_id:
                    self.new_room_message.image_id=image_id
                    message_data = "image"
                if message_data == "":
                    message_data="text"
                if not self.room_obj.activated :
                    self.room_obj.activated=True
                    self.room_obj.save()
                if not self.room_obj.group.status:
                    self.room_obj.group.status = True
                    self.room_obj.group.save()

                self.new_room_message.anonymous_user= self.room_obj.anon_customer
                self.new_room_message.save()
                file_urls = self.new_room_message.fils_urls()
                event = {
                "type": "create_new_message",
                "message_type": self.new_room_message.message_type,
                "body":self.new_room_message.body,
                "message_data":message_data,
                "message_type":"anonymous",
                "file_url":file_urls['file_url'],
                "voice_url":file_urls['voice_url'],
                "image_url":file_urls['image_url'],
                
                "created":self.new_room_message.jtime()
     
                
                
                }

        
                
                event['phone_number'] = self.new_room_message.anonymous_user.phone_number
                event['fullname']= self.new_room_message.anonymous_user.fullname
                event['message_id']= self.new_room_message.id


                async_to_sync(self.channel_layer.group_send)(
                str(self.room_id),event
                
                )


            elif command == "read a workspace":
                workspace_id = data.get('workspace_id')
                workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
                try:
                    group_obj = GroupRoom.objects.get(anon_customer=self.anon_user,workspace=workspace_obj)
             
                except:
                    group_obj = GroupRoom.objects.create(anon_customer=self.anon_user,workspace=workspace_obj)
                self.send(json.dumps(
                        {
                            "data_type":"group",
                            "data":self.make_workspace_room(group_room_obj=group_obj)
                        }
                    ))
            elif command == "read a message":
                message_id = data.get("message_id")
        elif self.side_type == "manager":
            if command == "read departments":
                workspace_id = data['workspace_id']
                workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
                departments = Department.objects.filter(workspace=workspace_obj )
                department_data = []
                for department in departments:
                    department_obj = {
                        "id":department.id,
                        "title":department.title,
                        "color_code":department.color_code,
                        "waiting":0,
                        "closed":0,
                        "confirmed":0,
                        "member_count":department.members.all().count()

                    }
                    rooms = Room.objects.filter(department=department,activated=True)
                    for room in rooms:
                        if room.room_status == "waiting":
                            department_obj['waiting']+=1

                        elif room.room_status == "closed":
                            department_obj['closed']+=1
                        elif room.room_status == "confirmed":
                            department_obj['confirmed'] +=1
                    department_data.append(department_obj)
                self.send(json.dumps({
                    "data_type":"department_list",
                    "data":department_data
                }))
            elif command == "create a department":
                title = data['title']
                color_code = data['color_code']
                workspace_id = data['workspace_id']
                member_list = data['member_list']
                workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
                new_department = Department(
                    title=title,
                    color_code=color_code,
                    workspace= workspace_obj
                )
                new_department.save()
                for member in member_list:
                    user_obj = UserAccount.objects.get(id=member)
                    new_department.members.add(user_obj)
                department_data ={
                    "id":department_obj.id,
                    "title":department_obj.title,
                    "color_code":department_obj.color_code,
                    "waiting":0,
                    "closed":0,
                    "confirmed":0,
                    "member_count":department_obj.members.all().count()
                }
                self.send(json.dumps({
                    "data_type":"department_obj",
                    "data":department_data
                }))

                

    def create_new_message(self,event):

        send_data ={
            "type":event['message_type'],
            "body":event['body'],
            "message_id":str(event['message_id']),
            "phone_number":event['phone_number'],
            "fullname":event['fullname'],
            "created":event['created'],
            "message_data":event['message_data'],
      
            "file_url":event['file_url'],
            "voice_url":event['voice_url'],
            "image_url":event['image_url'],
            
            
        }

        self.send(json.dumps(
            {
                "data_type":"room messages",
                "data":send_data
            }
        ))
    def paginate_queryset(self,page_number,room_obj):
        queryset = room_obj.messages.all().order_by("-id")
        
        # Set up custom pagination
        paginator = Paginator(queryset, 20)  # Set items per page

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

        message_list = []
        for message in page.object_list:
            dic = {
                "type": message.message_type,
                "body": message.body if message.body is not None else "",
                "id": str(message.id)
            }
            message_data = ""
            message_data_status=True
            if message.file:
                message_data = "file"
                dic['file_url'] = message.fils_urls()['file_url']
            elif message.voice :
                message_data="voice"
                dic['voice_url'] = message.fils_urls()['voice_url']

            elif message.image:
                message_data="image"
                dic['image_url'] = message.fils_urls()['image_url']
                
            else:
                message_data="text"
            dic['message_data'] =message_data
            if message.message_type == "anonymous":
                dic['phone_number'] = message.anonymous_user.phone_number
                dic['id'] = message.anonymous_user.id
                dic['fullname'] = message.anonymous_user.fullname
            else:
                dic['fullname'] = message.operator.fullname
                dic['id'] = message.operator.id
            message_list.append(dic)
        
        return {
            "count": paginator.count,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "data": message_list
        }



# class RoomMessageWs(WebsocketConsumer):
#     def connect(self):
        
#         self.room_id = self.scope['url_route']['kwargs']['room_id']

            
#         self.accept()
#         async_to_sync(self.channel_layer.group_add)(
#             str(self.room_id),
#             self.channel_name
#         )

  
#         self.room_obj = get_object_or_404(Room,id=self.room_id)
        
#     def disconnect(self,code=None):
        
#          async_to_sync(self.channel_layer.group_discard)(
#             str(self.room_id),
#             self.channel_name
#         )
#          self.close(code=0)
#     def receive(self,text_data=None):
#         data = json.loads(text_data)
#         if data['request_type'] == "read_messages":

#             page_number = data.get("page", 1)
#             message_data =  self.paginate_queryset(page_number)
#             self.send(json.dumps(message_data))
      
#         else:
           
#             self.new_message = RoomMessage(
#                 message_type = data['type'],
#                 body = data['body'],

#                 room = self.room_obj,

#             )

#             event = {
#                 "type": "create_new_message",
#                 "message_type": self.new_message.message_type,
#                 "body":self.new_message.body,
                
                
#             }

         
#             if data['type'] == "operator":
#                 self.new_message.operator_id =data['operator_id']
#                 event['operator_fullname'] = f"{self.new_message.operator.fullname}",
#                 event['operator_id'] = self.new_message.operator.id
#             else:
#                 self.new_message.anonymous_user_id=data['anonuser_id']
#                 self.new_message.anonymous_user= self.room_obj.anon_customer
#                 event['refrence_id'] = self.new_message.anonymous_user.refrence_id
#                 event['athor_id']= self.new_message.anonymous_user.id
            
#             self.new_message.save()
#             event['id'] = self.new_message.id

#             async_to_sync(self.channel_layer.group_send)(
#                 str(self.room_id),event
                
#             )
    
    
#     def test_pengination (self,event):
#         self.send(json.dumps(event['data']))
#     def paginate_queryset(self, page_number):
#         queryset = self.room_obj.messages.all().order_by("-id")
        
#         # Set up custom pagination
#         paginator = Paginator(queryset, 20)  # Set items per page

#         # Check if the requested page exists
#         if page_number > paginator.num_pages:
#             return {
#                 "count": paginator.count,
#                 "next": None,
#                 "previous": None,
#                 "data": []
#             }

#         # Get the page
#         page = paginator.get_page(page_number)

#         message_data = []
#         for message in page.object_list:
#             dic = {
#                 "type": message.message_type,
#                 "body": message.body if message.body is not None else "",
#                 "id": str(message.id)
#             }
#             if message.message_type == "anonymos":
#                 dic['refrence_id'] = message.anonymous_user.refrence_id
#                 dic['athor_id'] = message.anonymous_user.id
#             else:
#                 dic['fullname'] = f"{message.operator.first_name} {message.operator.last_name}"
#                 dic['athor_id'] = message.operator.id
#             message_data.append(dic)
        
#         return {
#             "count": paginator.count,
#             "next": page.next_page_number() if page.has_next() else None,
#             "previous": page.previous_page_number() if page.has_previous() else None,
#             "data": message_data
#         }

#     def create_new_message(self,event):

#         send_data ={
#             "type":event['message_type'],
#             "body":event['body'],
#             "id":str(event['id'])

#         }
#         if event['message_type'] == "anonymos":
#             send_data['refrence_id'] = event['refrence_id'] 
#             send_data['athor_id'] = event['athor_id']
#         else:
#             send_data['fullname'] = event['operator_fullname']
#             send_data['athor_id']= event['operator_id']
#         self.send(json.dumps(
#             {"data":send_data}
#         ))


# class RommWs(WebsocketConsumer):
#     def connect(self):
        
#         self.brand_name = self.scope['url_route']['kwargs']['username']

#         self.workspace_obj = get_object_or_404(WorkSpace,jadoo_brand_name=self.brand_name)

#         self.accept()
