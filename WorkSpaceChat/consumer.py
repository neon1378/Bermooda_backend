import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from WorkSpaceManager.models import WorkSpace
from .models import GroupMessage,TextMessage
from .serializers import GroupSerializer,TextMessageSerializer
from channels.layers import get_channel_layer
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import WorkSpace, GroupMessage, TextMessage
from .serializers import GroupSerializer, TextMessageSerializer


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

    @sync_to_async
    def _group_message_serialize(self):

        group_messages = GroupMessage.objects.filter(
            workspace=self.workspace_obj
        )
        data_list =[]
        for gp in group_messages :

            if self.user in gp.members.all():
                data_list.append(gp)
        print(self.user.id)
        print(data_list)
        serializer_data = GroupSerializer(data_list, many=True)

        for group in serializer_data.data:
            for member in group.get("members", []):
                member["self"] = member["id"] == self.user.id
        print(serializer_data.data)
        return serializer_data.data
    async def get_group_messages(self):

        data = await  self._group_message_serialize()
        print(data)
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
        else:
            await self.send(json.dumps({"data_type": "error", "data": serializer.errors}))

    async def send_group_message(self, event):
        message_obj = await sync_to_async(TextMessage.objects.get)(id=event["message_id"])
        serializer_data = await sync_to_async(lambda: TextMessageSerializer(message_obj).data)()
        serializer_data["self"] = event["owner_id"] == self.user.id

        await self.send(json.dumps({"data_type": "new_message", "data": serializer_data}))
