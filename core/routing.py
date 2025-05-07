from django.urls import path
from . import consumers
websocket_urlpatterns = [
    path("ws/UploadProgressConsumer/<upload_id>", consumers.UploadProgressConsumer.as_asgi()),
    path("ws/CoreBermooda/", consumers.CoreWebSocket.as_asgi()),

]