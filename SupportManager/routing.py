from django.urls import path
from . import consumers

websocket_urlpatterns = [
   
    # path("ws/ChatMessageWs/<str:phone_number>",consumers.ChatMessageWs.as_asgi()),
    path("ws/ChatMessageWs",consumers.ChatMessageWs.as_asgi()),

]