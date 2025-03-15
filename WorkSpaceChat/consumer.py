import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from django.core.paginator import Paginator

from WorkSpaceManager.models import WorkSpace
from .models import GroupMessage,TextMessage
from .serializers import GroupSerializer,TextMessageSerializer
from channels.layers import get_channel_layer
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import WorkSpace, GroupMessage, TextMessage
from .serializers import GroupSerializer, TextMessageSerializer
from collections import defaultdict
from django.db.models import F
import locale
import jdatetime

class GroupMessageWs(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close(code=1001)
            return

        self.user.is_online = True
        await sync_to_async(self.user.save)()

        self.workspace_id = self.user.current_workspace_id
        self.workspace_obj = await sync_to_async(WorkSpace.objects.get)(id=self.workspace_id)
        self.workspace_group_name = f"group_ws_{self.workspace_obj.id}"

        await self.channel_layer.group_add(self.workspace_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code=None):
        await self.channel_layer.group_discard(f"group_ws_{self.workspace_obj.id}", self.channel_name)

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
        elif command == "read_message_list":

            page_number = data["data"].get("page_number",1)


            await self.read_messages(

                page_number
            )

    @sync_to_async
    def _get_group_message_list(self,page_number):
        group_obj = GroupMessage.objects.get(id= self.group_id)
        read_messages = group_obj.group_text_messages.filter(is_read =False)
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
                "data": []
            }

        # Get the page
        page = paginator.get_page(page_number)





        # Group messages by date
        serializer_data =TextMessageSerializer(page.object_list,many=True)


        return {
            "count": paginator.count,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": serializer_data.data
        }



    async def read_messages(self,page_number):
        group_message_list = await self._get_group_message_list(page_number)
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
        data_list.sort(key=lambda gp: gp.last_message().created_at if gp.last_message() else None, reverse=True)
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
            await self.channel_layer.group_send(self.workspace_group_name, event)

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