from django.urls import path
from . import consumers
websocket_urlpatterns = [

    path("ws/ProjectChatWs/<project_id>",consumers.ProjectChatWs.as_asgi()),
    path("ws/ProjectTask/<project_id>",consumers.ProjectTaskConsumer.as_asgi()),

    path("ws/Project/GroupMessage/<project_id>",consumers.ProjectChatMainWs.as_asgi()),

    
]
    
    
