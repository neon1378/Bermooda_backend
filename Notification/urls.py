from django.urls import path
from . import views
urlpatterns = [
    path("test_notif",views.test_notif),
    path("NotifacticatonManager",views.NotifacticatonManager.as_view())
    
]
