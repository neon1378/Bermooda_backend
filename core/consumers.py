# consumers.py
import json

from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncWebsocketConsumer,AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from ProjectManager.models import Project,Task,CheckList,CategoryProject,ProjectMessage
from WorkSpaceManager.models import  WorkSpace,WorkspaceMember,WorkSpacePermission
from asgiref.sync import sync_to_async
from ProjectManager.serializers import TaskSerializer,CheckListSerializer,ProjectMessageSerializer
from UserManager.models import UserAccount
from .widgets import  pagination
from django.utils.timezone import is_naive, make_aware, get_current_timezone
import pytz
from Notification.models import Notification
from django.utils.timezone import make_aware
from CrmCore.models import CustomerUser,GroupCrm,Label,CustomerStep,GroupCrmMessage
from CrmCore.serializers import CustomerSmallSerializer,GroupCrmSerializer,LabelStepSerializer,GroupCrmMessageSerializer
from WorkSpaceChat.models import *
from WorkSpaceChat.serializers import *



# class UploadProgressConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Retrieve upload_id from the URL route.
#         self.upload_id = self.scope['url_route']['kwargs']['upload_id']
#
#         await self.channel_layer.group_add(self.upload_id, self.channel_name)
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.upload_id, self.channel_name)
#
#     async def upload_progress(self, event):
#         # Send the progress update to the WebSocket client.
#         progress = event['progress']
#         await self.send(text_data=json.dumps({
#             "data_type":"progress_status",
#             "progress_percentage":progress
#         }))
#


class CoreWebSocket(AsyncJsonWebsocketConsumer):
    """
    start the workspace 1 to 1 chat

    """
    # change user is_online
    @sync_to_async
    def change_user_online(self,status):

        user= UserAccount.objects.get(id=self.user.id)
        user.is_online=status
        user.save()


    @sync_to_async
    def _get_all_group_unread_messages(self):
        groups = GroupMessage.objects.filter(members=self.user,workspace= self.workspace_obj).only('id')
        return sum(group.unread_messages(user_id=self.user.id) for group in groups)


    @sync_to_async
    def _group_message_serialize(self):

        group_messages = GroupMessage.objects.filter(
            workspace=self.workspace_obj
        )
        data_list =[]
        for gp in group_messages:

            if self.user in gp.members.all():

                data_list.append(gp)

        def get_sort_key(gp):
            last_msg = gp.last_message()
            tehran_tz = pytz.timezone("Asia/Tehran")  # Explicit Tehran timezone

            if last_msg:
                created_at = last_msg.created_at

                # Ensure the datetime is timezone-aware
                if is_naive(created_at):
                    created_at = make_aware(created_at, timezone=tehran_tz)
                else:
                    created_at = created_at.astimezone(tehran_tz)  # Convert to Tehran time

                return created_at

            # Ensure datetime.min is also aware of Tehran timezone
            return make_aware(datetime.min, timezone=tehran_tz)

        data_list.sort(key=get_sort_key, reverse=True)

        serializer_data = GroupSerializer(data_list,many=True,context={'user': self.user})

        for group in serializer_data.data:
            for member in group.get("members", []):

                if member['id'] != self.user.id:
                    group['fullname'] = member['fullname']

                    group['avatar_url'] = member['avatar_url']
                    group['is_online'] = member['is_online']
                member["self"] = member["id"] == self.user
            group.pop("members")


        return serializer_data.data
    async def get_group_messages_handler(self,data):

        data = await  self._group_message_serialize()

        await self.send_json(
            {"data_type": "group_messages", "data": data}
        )


    @sync_to_async
    def _send_new_message(self,data):
        text =  data.get("text")

        group_id = data.get("group_id")



        message_obj = TextMessage.objects.create(
            owner_id=self.user.id,
            group_id=group_id,
            text=text
        )
        return {
                "status":True,
                "data":{
                    "message_id":message_obj.id,
                }
            }
        # serializer_data = TextMessageSerializer(data={
        #     "owner_id": self.user.id,
        #     "group_id": group_id,
        #     "text": text,
        # })

        # if serializer_data.is_valid():
        #     message_obj = serializer_data.save()
        #     return {
        #         "status":True,
        #         "data":{
        #             "message_id":message_obj.id,
        #         }
        #     }
        # return {
        #     "status":False,
        #     "data":serializer_data.errors
        # }
    async def new_message_handler(self, data):
        group_id = data.get("group_id")
        group_name = f"group_message{group_id}"
        new_message = await self._send_new_message(data=data)
        if new_message['status']:



            event = {
                "type": "send_group_message",
                "message_id": new_message["data"]["message_id"],
                "owner_id": self.user.id,
            }

            await self.channel_layer.group_send(group_name, event)

            event = {
                "type":"send_groups"
            }

            await self.channel_layer.group_send(group_name, event)

            event = {
                "type":"send_all_unread_messages"
            }
            await self.channel_layer.group_send(group_name, event)

        else:
            await self.send_json(
                {"data_type": "error", "data": new_message['data']}
            )

    async def send_all_unread_messages(self,event):
        message_count = await self._get_all_group_unread_messages()
        await self.send_json(
        {
                "data_type": "all_group_message_unread",
                "data": {
                    "message_count": message_count
                }
            }
        )

    @sync_to_async
    def _new_message_check_read(self,event):
        message_obj =  TextMessage.objects.get(id=event["message_id"])
        if not message_obj.owner == self.user:
            message_obj.is_read = True
            message_obj.save()
        serializer_data =  TextMessageSerializer(message_obj).data
        serializer_data["self"] = event["owner_id"] == self.user.id
        return serializer_data

    async def send_group_message(self, event):
        message_data = await  self._new_message_check_read(event=event)

        await self.send_json(
            {"data_type": "new_message", "data": message_data}
        )

    async def send_groups(self,event):
        group_data = await self._group_message_serialize()

        await self.send_json(
            {"data_type": "group_messages", "data": group_data}
        )
    async def get_unread_messages_handler(self,data):

        await self.channel_layer.group_send(self.user_group_name, {"type": "send_all_unread_messages"})

    @sync_to_async
    def _get_group_message_list(self,page_number,group_id):
        group_obj = GroupMessage.objects.get(id= group_id)
        read_messages = group_obj.group_text_messages.filter(is_read =False)
        message_count = group_obj.group_text_messages.all().count()

        for message in read_messages:
            if message.owner != self.user:
                message.is_read = True
                message.save()

        text_messages = group_obj.group_text_messages.all().order_by("-id")

        paginator = Paginator(text_messages, 20)  # Set items per page

        # Check if the requested page exists
        if int(page_number) > paginator.num_pages:
            return {
                "count": paginator.count,
                "next": None,
                "previous": None,
                "group_id":group_id,
                "list": []
            }

        # Get the page
        page = paginator.get_page(page_number)





        # Group messages by date
        serializer_data =TextMessageSerializer(page.object_list,many=True)

        for message_data in serializer_data.data:
            message_data['self'] = message_data['owner']['id'] == self.user.id
        return {
            "count": paginator.count,
            "group_id": group_id,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": serializer_data.data
        }



    async def read_message_list_handler(self,data):
        page_number = data.get("page_number",1)
        group_id = data.get("group_id")
        group_message_list = await self._get_group_message_list(page_number,group_id)
        print(group_message_list,"@22")
        event = {
            "type": "send_groups"
        }
        await self.channel_layer.group_send(self.user_group_name, event)
        await self.send_json(
            {
                "data_type": "message_list",
                "data": group_message_list
            }
        )
    @sync_to_async
    def _get_workspace_data(self, workspace_id):
        current_workspace_obj = WorkSpace.objects.get(id=workspace_id)
        data = {
            "wallet": {
                "id": current_workspace_obj.wallet.id if current_workspace_obj.wallet else None,
                "balance": int(current_workspace_obj.wallet.balance) if current_workspace_obj.wallet else 0
            },
            "auth_status": current_workspace_obj.auth_status,
            "id": current_workspace_obj.id,
            "title": current_workspace_obj.title,
            "is_authenticated": current_workspace_obj.is_authenticated,
            "jadoo_workspace_id": current_workspace_obj.jadoo_workspace_id,
            "is_active": current_workspace_obj.is_active,
            "workspace_permissions": [
                {
                    "id": permission.id,
                    "permission_type": permission.permission_type,
                    "is_active": permission.is_active
                } for permission in WorkSpacePermission.objects.filter(workspace=current_workspace_obj)
            ],
            "unread_notifications": Notification.objects.filter(
                workspace=current_workspace_obj,
                user_account=self.user,
                is_read=False
            ).count() + Notification.objects.filter(user_account=self.user, is_read=False).count()
        }

        if self.user == current_workspace_obj.owner:
            data["type"] = "owner"
        else:
            try:
                workspac_member = WorkspaceMember.objects.get(
                    workspace=current_workspace_obj,
                    user_account=self.user  # Use self.user consistently
                )
                data["permissions"] = [
                    {
                        "id": permission.id,
                        "permission_name": permission.permission_name,
                        "permission_type": permission.permission_type
                    } for permission in workspac_member.permissions.all()
                ]
                data["is_accepted"] = workspac_member.is_accepted
            except WorkspaceMember.DoesNotExist:
                pass
            data["type"] = "member"

        return data
    async def change_current_workspace(self, event):

        self.workspace_id = event['workspace_id']
        self.workspace_obj = await self._get_workspace_obj()
        self.workspace_group_name = f"group_ws_{self.workspace_obj.id}"

        # Notify the user group to update groups and unread messages
        await self.channel_layer.group_send(self.user_group_name, {"type": "send_groups"})
        await self.channel_layer.group_send(self.user_group_name, {"type": "send_all_unread_messages"})
        await self.channel_layer.group_send(self.user_group_name, {"type": "send_wallet_detail_data"})


        # Send updated workspace data to the client
        current_workspace = await self._get_workspace_data(self.workspace_id)
        await self.send(json.dumps({
            "data_type": "change_current_workspace",
            "data": {
                "current_workspace": current_workspace
            }
        }))


    """
     end to workspace 1 to 1 chat
     
    """

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:

            await self.close(code=4001)
            return

        await self.accept()

        self.user_group_name = f"{self.user.id}_gp_user"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        self.workspace_obj = await self._get_workspace_obj()
        unread_message_count = await self._get_all_group_unread_messages()
        await self.change_user_online(status=True)
        await self.send_json(
            {
                "data_type": "all_group_message_unread",
                "data": {
                    "message_count": unread_message_count
                }
            }
        )

    @sync_to_async
    def _get_workspace_obj(self):
        user_account = UserAccount.objects.get(id=self.user.id)
        workspace_obj = WorkSpace.objects.get(id=user_account.current_workspace_id)
        return workspace_obj
    async def disconnect(self, close_code):
        await self.change_user_online(status=False)
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def send_extra(self,data):
        event = {
            "type":"send_event_task_list",
            "project_id":data.get("project_id"),
        }
        await self.channel_layer.group_send(
            self.project_group_name,
            event
        )
    async def receive_json(self, content, **kwargs):
        command = content.get("command")
        print(content)
        data = content.get("data",None)

        command_handlers = {
            'task_list': self.handle_task_list,
            'move_a_task': self.handle_move_task,
            'change_sub_task_status': self.handle_subtask_status,

            'change_task_status': self.handle_task_status,

            "read_all_messages": self.read_all_messages,

            "create_a_message": self.create_a_message_handler,

            "edit_message": self.edit_message_handler,

            # Crm WebSocket Commands
            "customer_list":self.customer_list_handler,
            "move_a_customer": self.move_a_customer_handler,

            "change_step_status":self.change_step_status_handler,

            "change_is_followed":self.change_is_followed_handler,

            "crm_read_all_messages":self.crm_read_all_messages_handler,
            "crm_create_a_message":self.crm_create_a_message_handler,
            "crm_edit_message":self.crm_edit_message_handler,
            # "send_extra":self.send_extra,
            # < < < begin workspace 1 to 1 chat command > > > #

            "get_group_messages":self.get_group_messages_handler,

            "new_message":self.new_message_handler,
            "get_unread_messages":self.get_unread_messages_handler,
            "read_message_list":self.read_message_list_handler,
            "wallet_detail":self.wallet_detail_handler,
            # < < < end workspace 1 to 1 chat command > > > #
        }
        handler = command_handlers.get(command)

        if handler:
            if command == "task_list" or command == "read_all_messages":
                project_id = data.get("project_id")
                self.project_group_name = f"{project_id}_gp_project"

                await self.channel_layer.group_add(
                    self.project_group_name,
                    self.channel_name
                )
            if command == "customer_list":
                group_crm_id = data.get("group_crm_id")
                self.crm_group_name = f"{group_crm_id}_gp_group_crm"
                await self.channel_layer.group_add(
                    self.crm_group_name,
                    self.channel_name
                )
            if command == "read_message_list":
                group_id = data.get("group_id")
                self.group_message_name = f"group_message{group_id}"
                await self.channel_layer.group_add(self.group_message_name, self.channel_name)
            await handler(data)
        else:
            await self.send_error("Invalid command")

    async def send_error(self, message):
        """Helper method for sending error messages"""
        await self.send_json({
            "data_type": "error",
            "message": message,
            "data": {}
        })
    #wallet Detail Begin
    @sync_to_async
    def wallet_detail_data (self):
        return {
            "id":self.workspace_obj.wallet.id,
            "balance":int(self.workspace_obj.wallet.balance) if self.workspace_obj.wallet.balance else 0,
        }

    async def wallet_detail_handler(self,data):
        wallet_data = await self.wallet_detail_data()
        await self.send_json(
            {
                "data_type":"wallet_detail",
                "data":wallet_data
            }
        )
    async def send_wallet_detail_data(self,event):
        wallet_data = await self.wallet_detail_data()
        await self.send_json(
            {
                "data_type": "wallet_detail",
                "data": wallet_data
            }
        )

    # Crm Customer Begin
    async def change_step_status_handler(self,data):
        group_crm_id = data.get("group_crm_id")

        step_obj = await self._change_step_status(main_data=data)

        event = {
            'type': 'send_customer_list',
            "group_crm_id":group_crm_id
        }

        await self.channel_layer.group_send(
            f"{group_crm_id}_gp_group_crm",
            event
        )

    @sync_to_async
    def _change_step_status(self,main_data):

        step = int(main_data['step'])
        customer_obj = CustomerUser.objects.get(id=main_data['customer_id'])
        step_obj = None
        for step_item in customer_obj.label.label_step.steps.all():
            if step_item.step == step:
                step_obj = step_item

        new_step_customer = CustomerStep.objects.create(
            customer=customer_obj,
            label=customer_obj.label,
            step=step_obj
        )
        return new_step_customer

    async def send_customer_list(self,event):
        serializer_data = await self._customer_list_serializer(group_crm_id=event['group_crm_id'])
        await self.send_json(
            {
                "data_type": "customer_list",
                "data": serializer_data
            }
        )
    async def customer_list_handler(self,data):
        group_crm_id=data.get("group_crm_id")
        customer_data = await self._customer_list_serializer(group_crm_id=group_crm_id)

        payload = {
            'data_type': 'customer_list',
            'data': customer_data,
        }
        await self.send_json(payload)
    @sync_to_async
    def _get_user_permission(self):
        workspace= self.workspace_obj

        if self.user == workspace.owner:
            return True
        workspace_member =WorkspaceMember.objects.get(user_account = self.user,workspace=workspace)
        for permission in workspace_member.permissions.all():
            if permission.permission_name == "crm":
                if permission.permission_type == "manager":
                    return True
                else:
                    return False

    @sync_to_async
    def _customer_list_serializer(self, group_crm_id):
        user_permission = self._get_user_permission()
        if user_permission:
            customer_objs = CustomerUser.objects.filter(group_crm_id=group_crm_id, is_followed=False)
        else:
            customer_objs = CustomerUser.objects.filter(group_crm_id=group_crm_id, is_followed=False,
                                                        user_account=self.user)

        data_list = []
        no_label_customers = []

        for customer_obj in customer_objs:
            if not customer_obj.label:
                no_label_customers.append(CustomerSmallSerializer(customer_obj).data)
                continue

            # Normal labeled customer handling
            not_exists = True
            for data in data_list:
                if data['label_id'] == customer_obj.label.id:
                    data['customer_list'].append(CustomerSmallSerializer(customer_obj).data)
                    not_exists = False
                    break

            if not_exists:
                data_list.append({
                    "label_id": customer_obj.label.id,
                    "color": customer_obj.label.color,
                    "title": customer_obj.label.title,
                    "steps": LabelStepSerializer(customer_obj.label.label_step.steps.all(), many=True).data,
                    "group_crm_id": group_crm_id,
                    "customer_list": [CustomerSmallSerializer(customer_obj).data]
                })

        # Handle label entries that have no customers
        label_objs = Label.objects.filter(group_crm_id=group_crm_id).order_by("-id")
        for label in label_objs:
            if not any(data['label_id'] == label.id for data in data_list):
                data_list.append({
                    "label_id": label.id,
                    "color": label.color,
                    "title": label.title,
                    "group_crm_id": group_crm_id,
                    "steps": LabelStepSerializer(label.label_step.steps.all(), many=True).data,
                    "customer_list": []
                })

        # Add a group for customers without a label

        data_list.append({
                "label_id": None,
                "color": None,
                "title": "لیست  اتتظار",
                "group_crm_id": group_crm_id,
                "steps": [],
                "customer_list": no_label_customers
            })

        return sorted(data_list, key=lambda x: (x["label_id"] is None, x["label_id"]))

    async def move_a_customer_handler(self,data):
        group_crm_id = data.get("group_crm_id")
        customer_obj = await self._move_a_customer(main_data=data)

        event = {
            'type': 'send_customer_list',
            "group_crm_id":group_crm_id
        }

        await self.channel_layer.group_send(
            f"{group_crm_id}_gp_group_crm",
            event
        )



    @sync_to_async
    def _move_a_customer(self,main_data):

        customer_obj = CustomerUser.objects.get(id=main_data['customer_id'])

        label_obj = Label.objects.get(id=main_data['label_id'])
        customer_obj.label = label_obj

        customer_obj.save()
        for order_data in main_data['customer_orders']:
            customer_order = CustomerUser.objects.get(id=order_data['customer_id'])
            customer_order.order = order_data['order']
            customer_order.save()

        return customer_obj

    async def change_is_followed_handler(self,data):
        group_crm_id = data.get("group_crm_id")
        customer_obj = await self._change_customer_is_followed(main_data=data)
        event = {
            'type': 'send_customer_list',
            "group_crm_id":group_crm_id
        }

        await self.channel_layer.group_send(
            f"{group_crm_id}_gp_group_crm",
            event
        )


    @sync_to_async
    def _change_customer_is_followed(self, main_data):
        customer_id = main_data['customer_id']
        customer_obj = get_object_or_404(CustomerUser, id=customer_id)
        customer_obj.is_followed = main_data['is_followed']
        customer_obj.save()
        return customer_obj
    #crm Group Message Begin



    @sync_to_async
    def _crm_all_message_serializer(self,group_crm_id,page_number,per_page_count=None):
        message_objs = GroupCrmMessage.objects.filter(group_crm_id=group_crm_id).order_by("-id")
        if per_page_count:
            pagination_data = pagination(
                query_set=message_objs,
                page_number=page_number,
                per_page_count=per_page_count
            )
        else:
            pagination_data = pagination(
                query_set=message_objs,
                page_number=page_number,

            )
        pagination_data["list"] = GroupCrmMessageSerializer(pagination_data["list"],many=True,context={"user":self.user}).data
        pagination_data['group_crm_id'] = group_crm_id
        return pagination_data

    async def crm_read_all_messages_handler(self,data):
        group_crm_id = data.get("group_crm_id")
        try:

            page_number= data.get("page_number",1)
            per_page_count = data.get("per_page_count",None)
        except:
            per_page_count = None
            page_number = 1
        message_data = await self._crm_all_message_serializer(
            page_number=page_number,
            group_crm_id=group_crm_id,
            per_page_count=per_page_count
        )
        await self.send_json(
            {
                "data_type": "crm_all_messages",
                "data": message_data
            }
        )

    @sync_to_async
    def _crm_create_a_message(self, data):
        group_crm_id = data.get("group_crm_id")


        data['creator_id'] = self.user.id
        serializer_data = GroupCrmMessageSerializer(data=data)

        if serializer_data.is_valid():
            message_obj = serializer_data.save()
            return {
                "status": True,
                "data": {
                    "message_id": message_obj.id
                }
            }

        return {
            "status": False,
            "data": serializer_data.errors
        }

    async def crm_create_a_message_handler(self,data):
        group_crm_id = data.get("group_crm_id")
        message_data = await self._crm_create_a_message(data=data)

        if message_data['status']:

            event = {
                'type': 'crm_send_a_message',
                "message_id": message_data['data']['message_id']
            }

            await self.channel_layer.group_send(
                f"{group_crm_id}_gp_group_crm",
                event
            )


        else:
            await self.send_json(
                {
                    "data_type": "Validation Error",
                    "data": message_data['data']
                }
            )

    @sync_to_async
    def _crm_one_message_serializer(self,message_id):
        message_obj = get_object_or_404(GroupCrmMessage,id=message_id)
        serializer_data = GroupCrmMessageSerializer(message_obj,context={"user":self.user})
        return serializer_data.data

    async def crm_send_a_message(self,event):

        message_data = await self._crm_one_message_serializer(message_id=event['message_id'])
        await self.send_json(
            {
                "data_type": "crm_send_a_message",
                "data": message_data

            }
        )

    @sync_to_async
    def _crm_edit_a_message(self,data):

        message_obj = get_object_or_404(GroupCrmMessage,id=data['message_id'])
        message_obj.body = data['body']
        message_obj.save()
        return {
            "status":True,
            "data":{
                "message_id":message_obj.id
            }
        }
    async def crm_edit_message_handler(self,data):
        group_crm_id = data.get("group_crm_id")
        message_data = await self._crm_edit_a_message(data=data)
        event = {
            'type': 'crm_send_a_message',
            "message_id": message_data['data']['message_id']
        }

        await self.channel_layer.group_send(
            f"{group_crm_id}_gp_group_crm",
            event
        )

    # Crm Group Message  End


    #Crm Customer End


    # Project Task Begin

    #Project Message Begin
    @sync_to_async
    def _all_message_serializer(self,page_number,project_id,per_page_count=None):

        message_objs = ProjectMessage.objects.filter(project_id=project_id).order_by("-id")
        if per_page_count:
            pagination_data = pagination(query_set=message_objs,page_number=page_number,per_page_count=per_page_count)
        else:
            pagination_data = pagination(query_set=message_objs,page_number=page_number)


        pagination_data['current_page'] = page_number
        pagination_data['list'] = ProjectMessageSerializer(pagination_data['list'],many=True,context={"user":self.user}).data
        pagination_data['project_id'] = project_id
        return pagination_data
    async def read_all_messages(self,data):
        project_id = data.get("project_id")
        try:

            page_number= data.get("page_number",1)
            per_page_count = data.get("per_page_count",None)
        except:
            per_page_count = None
            page_number = 1

        message_data = await self._all_message_serializer(project_id=project_id,page_number=page_number,per_page_count=per_page_count)
        await self.send_json(
            {
                "data_type": "all_messages",
                "data": message_data
            }
        )
    @sync_to_async
    def _create_a_message(self,data):
        project_id = data.get("project_id")


        data['creator_id'] = self.user.id
        serializer_data =ProjectMessageSerializer(data=data,context={"user":self.user})
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
    async def create_a_message_handler(self,data):
        project_id = data.get("project_id")
        message_data = await self._create_a_message(data=data)
        if message_data['status']:
            event = {
                "type": "send_a_message",

                "message_id": message_data['data']['message_id']
            }
            project_group_name = f"{project_id}_gp_project"
            await self.channel_layer.group_send(
                project_group_name,
                event
            )

        else:
            await self.send_json(
                {
                    "data_type": "Validation Error",
                    "data": message_data['data']
                }
            )
    @sync_to_async
    def _one_message_serializer(self,message_id):
        message_obj = get_object_or_404(ProjectMessage,id=message_id)
        serializer_data = ProjectMessageSerializer(message_obj,context={"user":self.user})
        return serializer_data.data
    async def send_a_message(self,event):

        message_data = await self._one_message_serializer(message_id=event['message_id'])
        await self.send_json(
            {
                "data_type": "send_a_message",
                "data": message_data

            }
        )
    @sync_to_async
    def _edit_a_message(self,data):

        message_obj = get_object_or_404(ProjectMessage,id=data['message_id'])
        message_obj.body = data['body']
        message_obj.save()
        return {
            "status":True,
            "data":{
                "message_id":message_obj.id
            }
        }
    async def edit_message_handler(self,data):
        project_id = data.get("project_id")
        message_data = await self._edit_a_message(data=data)
        event = {
            "type": "send_a_message",

            "message_id": message_data['data']['message_id']
        }
        project_group_name = f"{project_id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )

    #Project Message End
    async def handle_task_status(self, data):
        project_id = data.get("project_id")
        """Handle main task status changes"""
        task = await sync_to_async(get_object_or_404)(Task, id=data['task_id'])

        if not self._has_admin_access():
            raise PermissionDenied("Access denied")

        task.done_status = data['done_status']
        await sync_to_async(task.save)()

        event = {
            "type": "send_event_task_list",

            "project_id": project_id
        }
        project_group_name = f"{project_id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )
    async def handle_subtask_status(self, data):
        """Handle subtask status changes"""
        project_id =data.get("project_id")
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

        event = {
            "type": "send_one_task",
            "task_id": task_obj.id,
        }
        project_group_name = f"{project_id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )

    @sync_to_async
    def _move_a_task_logic(self,data):
        category_id = data.get("category_id")
        task_id = data.get("task_id")
        orders_task=data.get("orders_task")
        category = get_object_or_404(CategoryProject,id=category_id)
        task = get_object_or_404(Task,id=task_id)
        task.category_task=category
        task.save()
        for order_data in orders_task:

            task_obj = Task.objects.get(id=order_data['task_id'])
            task_obj.order= order_data['order']
            task_obj.save()
        return task
    async def handle_move_task(self, data):
        project_id = data.get("project_id")
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

        event = {
            "type":"send_one_task",
            "task_id":data['task_id'],
        }
        project_group_name = f"{project_id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )


    async def send_one_task(self, event):


        task_data = await self._one_task_serializer(task_id=event['task_id'])

        await self.send_json({
            "data_type": "get_a_task",
            "data": task_data
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
    async def handle_task_list(self, data):
        project_id = data.get("project_id")



        """Handle task list refresh requests"""
        data = await self._main_serializer_data(project_id = project_id)
        await self.send_json({
            "data_type": "task_list",
            "data": data
        })

    @sync_to_async(thread_sensitive=True)
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

    @sync_to_async(thread_sensitive=True)
    def _has_admin_access(self):

        """Check if user has admin-level permissions"""
        if  self.workspace_obj.owner == self.user:
            return True
        else:
            if self._get_permission_type() == "manager":
                return True
            return False
        # return (
        #         self.workspace_obj.owner == self.user or
        #         self._get_permission_type() == "manager"
        # )

    @sync_to_async(thread_sensitive=True)
    def _get_filtered_tasks(self,project_id):
        """Optimized task fetching with smart prefetching."""
        base_qs = Task.objects.filter(
            project_id=project_id,
            done_status=False
        ).select_related('category_task').prefetch_related(
            Prefetch('check_list',
                     queryset=CheckList.objects.select_related('responsible_for_doing'))
        )


        if not self._has_admin_access():

            task_list = []
            for task in base_qs:
                for check_list in task.check_list.all():
                    if check_list.responsible_for_doing == self.user:
                        task_list.append(task)
                        break
            return task_list
        else:
            return base_qs

    async def send_event_task_list(self, event):
        project_id = event['project_id']
        data = await self._main_serializer_data(project_id = project_id)
        """Handler for group send events"""
        await self.send_json({
            "data_type": "task_list",
            "data": data
        })

    @sync_to_async(thread_sensitive=True)
    def _main_serializer_data(self, project_id):
        """Generate structured task data with categories more efficiently."""
        # Fetch all categories in a single query
        category_objs = CategoryProject.objects.filter(project_id=project_id).order_by("-id")
        all_categories = {cat.id: cat for cat in category_objs}

        # Get tasks with optimized related data fetching
        task_objs = self._get_filtered_tasks(project_id=project_id)

        # Serialize tasks, leveraging pre-fetched related data
        serializer_data = TaskSerializer(task_objs, many=True)

        # Organize tasks by category using serializer data
        categories = {}
        uncategorized_tasks = []  # collect tasks with no category

        for task in serializer_data.data:
            if task['category_task']:
                category_id = task['category_task']['id']
                if category_id not in all_categories:
                    continue  # Skip invalid categories (data integrity issue)

                # Use category data from serializer to maintain compatibility
                category_data = task["category_task"]
                if category_id not in categories:
                    categories[category_id] = {
                        "category_id": category_id,
                        "project_id": project_id,
                        "color": category_data['color_code'],
                        "title": category_data['title'],
                        "task_list": []
                    }
                categories[category_id]['task_list'].append(task)
            else:
                uncategorized_tasks.append(task)

        # Fill in empty categories from pre-fetched data
        for category in category_objs:
            if category.id not in categories:
                categories[category.id] = {
                    "category_id": category.id,
                    "color": category.color_code,
                    "project_id": project_id,
                    "title": category.title,
                    "task_list": []
                }

        # Add uncategorized tasks to a special category

        categories[None] = {
                "category_id": None,
                "color": None,
                "project_id": project_id,
                "title": "لیست انتظار",
                "task_list": uncategorized_tasks
        }

        # Return sorted results
        return sorted(categories.values(), key=lambda x: (x['category_id'] is None, x['category_id']))

    # @sync_to_async
    # def _main_serializer_data(self,project_id):
    #     return self._main_serializer_data_sync(project_id)
    # # Project Task End




# consumers.py



