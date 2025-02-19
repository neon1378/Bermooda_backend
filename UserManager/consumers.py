
import django
django.setup()
import json 
from channels.generic.websocket import WebsocketConsumer

class WebSocketTest(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            self.accept()
        else:
            self.close(0)

        
        self.send(json.dumps(
            {
                "type":"succses"
            }
        ))
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        print(type(data))
        self.send(json.dumps({
            "message":data['message'],
            "type":"fuck you"
        }))