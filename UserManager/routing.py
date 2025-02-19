from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("test/",consumers.WebSocketTest.as_asgi())
]