import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django
import ProjectManager.routing as project_manager
import SupportManager.routing as SuportManager
import CrmCore.routing  as CrmManager
import WorkSpaceChat.routing as WorkSpaceChat
from .middleware import TokenAuthMiddleware,JWTAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CrmManager.settings')
routers = SuportManager.websocket_urlpatterns + project_manager.websocket_urlpatterns + CrmManager.websocket_urlpatterns +WorkSpaceChat.websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            routers
        )
    ),
})
