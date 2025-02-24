from django.urls import path
from .consumer import  *
websocket_urlpatterns=[
    path("ws/GroupMessageWs",GroupMessageWs.as_asgi())

]