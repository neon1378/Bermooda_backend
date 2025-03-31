# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UploadProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve upload_id from the URL route.
        self.upload_id = self.scope['url_route']['kwargs']['upload_id']
        print(self.upload_id)
        await self.channel_layer.group_add(self.upload_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.upload_id, self.channel_name)

    async def upload_progress(self, event):
        # Send the progress update to the WebSocket client.
        progress = event['progress']
        await self.send(text_data=json.dumps({
            "data_type":"progress_status",
            "progress_percentage":progress
        }))
