from django.urls import path
from . import consumers

websocket_urlpatterns = [

    path("ws/CustomerTask/<group_crm_id>", consumers.CustomerTaskMain.as_asgi()),


]

