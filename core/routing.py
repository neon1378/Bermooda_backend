from django.urls import path
from . import consumers
websocket_urlpatterns = [

    path("ws/CoreBermooda", consumers.CoreWebSocket.as_asgi()),

    # path("ws/vpn", consumers.VPNProxyConsumer.as_asgi()),

]