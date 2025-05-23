import json
from UserManager.models import UserAccount
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from django.core.paginator import Paginator

from django.utils.timezone import localtime
from django.utils.timezone import is_naive, make_aware, get_current_timezone
from datetime import datetime
import pytz
from pkg_resources import working_set
from WorkSpaceManager.models import WorkSpace,WorkspaceMember,WorkSpacePermission

from Notification.models import Notification
from WorkSpaceManager.models import WorkSpace
from .models import GroupMessage,TextMessage
from .serializers import GroupSerializer,TextMessageSerializer
from channels.layers import get_channel_layer
import json
from django.utils.timezone import make_aware
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import WorkSpace, GroupMessage, TextMessage
from .serializers import GroupSerializer, TextMessageSerializer
from collections import defaultdict
from django.db.models import F
import locale
import jdatetime

class GroupMessageWs(AsyncWebsocketConsumer):

    @sync_to_async
    def change_user_online(self,status):

        user= UserAccount.objects.get(id=self.user.id)
        user.is_online=status
        user.save()


    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close(code=1001)
            return
        #
        # self.user.is_online = True
        # await sync_to_async(self.user.save)()
        await self.change_user_online(status=True)
        self.workspace_id = self.user.current_workspace_id
        self.workspace_obj = await self.get_workspace_obj()

        self.user_group_name = f"user_group_{self.user.id}"

        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        message_count = await self._get_all_group_unread_messages()


        # await self.channel_layer.group_send(self.user_group_name, {
        #     "type": "change_current_workspace",
        #     "workspace_id": self.workspace_id
        # })
        await self.send(json.dumps(
            {
                "data_type": "all_group_message_unread",
                "data": {
                    "message_count": message_count
                }
            }
        ))

    @sync_to_async
    def get_workspace_obj(self):

        workspace_obj = WorkSpace.objects.get(id=self.workspace_id)
        return workspace_obj
    @sync_to_async
    def _get_all_group_unread_messages(self):
        groups = GroupMessage.objects.filter(members=self.user,workspace= self.workspace_obj).only('id')
        return sum(group.unread_messages(user_id=self.user.id) for group in groups)

    async def send_all_unread_messages(self,event):
        message_count = await self._get_all_group_unread_messages()
        await self.send(json.dumps({
            "data_type":"all_group_message_unread",
            "data":{
                "message_count":message_count
            }
        })
        )

    @sync_to_async
    def _get_workspace_data(self, workspace_id):
        current_workspace_obj = WorkSpace.objects.get(id=workspace_id)
        data = {
            "wallet": {
                "id": current_workspace_obj.wallet.id if current_workspace_obj.wallet else None,
                "balance": int(current_workspace_obj.wallet.balance) if current_workspace_obj.wallet else 0
            },
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
        self.workspace_obj = await self.get_workspace_obj()
        self.workspace_group_name = f"group_ws_{self.workspace_obj.id}"

        # Notify the user group to update groups and unread messages
        await self.channel_layer.group_send(self.user_group_name, {"type": "send_groups"})
        await self.channel_layer.group_send(self.user_group_name, {"type": "send_all_unread_messages"})

        # Send updated workspace data to the client
        current_workspace = await self._get_workspace_data(self.workspace_id)
        await self.send(json.dumps({
            "data_type": "change_current_workspace",
            "data": {
                "current_workspace": current_workspace
            }
        }))


    async def disconnect(self, code=None):
        #
        # self.user.is_online = False
        # await sync_to_async(self.user.save)()
        await self.change_user_online(status=False)
        await self.channel_layer.group_discard(f"user_group_{self.user.id}", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        data = json.loads(text_data)
        command = data.get("command")


        if command == "get_group_messages":
            await self.get_group_messages()
        elif command == "open_a_group_message":
            await self.open_group_message(data["data"].get("group_id"))
        elif command == "close_a_group_message":
            await self.close_group_message()
        elif command == "new_message":
            await self.new_message(data["data"].get("text"))
        elif command == "get_unread_messages" :
            await self.channel_layer.group_send(self.user_group_name, {"type": "send_all_unread_messages"})
        elif command == "read_message_list":

            page_number = data["data"].get("page_number",1)


            await self.read_messages(

                page_number
            )

    @sync_to_async
    def _get_group_message_list(self,page_number):
        group_obj = GroupMessage.objects.get(id= self.group_id)
        read_messages = group_obj.group_text_messages.filter(is_read =False)
        message_count = group_obj.group_text_messages.all().count()
        print(message_count)
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
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": serializer_data.data
        }



    async def read_messages(self,page_number):
        group_message_list = await self._get_group_message_list(page_number)
        event = {
            "type": "send_groups"
        }
        await self.channel_layer.group_send(self.user_group_name, event)
        await self.send(json.dumps(
            {
                "data_type":"message_list",
                "data":group_message_list
            }
        ))

    @sync_to_async
    def _group_message_serialize(self):

        group_messages = GroupMessage.objects.filter(
            workspace=self.workspace_obj
        )
        data_list =[]
        for gp in group_messages :

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
    async def get_group_messages(self):

        data = await  self._group_message_serialize()

        await self.send(json.dumps({"data_type": "group_messages", "data": data}))

    async def open_group_message(self, group_id):
        if not group_id:
            return

        self.group_id = group_id
        self.group_message_name = f"group_message{self.group_id}"
        await self.channel_layer.group_add(self.group_message_name, self.channel_name)

    async def close_group_message(self):
        if hasattr(self, "group_message_name"):
            await self.channel_layer.group_discard(self.group_message_name, self.channel_name)

    async def new_message(self, text):
        if not text or not hasattr(self, "group_id"):
            return

        serializer = TextMessageSerializer(data={
            "owner_id": self.user.id,
            "group_id": self.group_id,
            "text": text,
        })

        if serializer.is_valid():
            await sync_to_async(serializer.save)()
            message_obj = await sync_to_async(lambda: serializer.data)()

            event = {
                "type": "send_group_message",
                "message_id": message_obj["id"],
                "owner_id": self.user.id,
            }

            await self.channel_layer.group_send(self.group_message_name, event)

            event = {
                "type":"send_groups"
            }

            await self.channel_layer.group_send(self.user_group_name, event)

            event = {
                "type":"send_all_unread_messages"
            }
            await self.channel_layer.group_send(self.user_group_name, event)

        else:
            await self.send(json.dumps({"data_type": "error", "data": serializer.errors}))

    @sync_to_async
    def _send_message_handler(self,event):
        message_obj =  TextMessage.objects.get(id=event["message_id"])
        if not message_obj.owner == self.user:
            message_obj.is_read = True
            message_obj.save()
        serializer_data =  TextMessageSerializer(message_obj).data
        serializer_data["self"] = event["owner_id"] == self.user.id
        return serializer_data

    async def send_group_message(self, event):
        message_data = await  self._send_message_handler(event=event)

        await self.send(json.dumps({"data_type": "new_message", "data": message_data}))

    async def send_groups(self,event):
        group_data = await self._group_message_serialize()

        await self.send(json.dumps({"data_type": "group_messages", "data": group_data}))