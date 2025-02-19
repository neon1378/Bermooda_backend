from django.urls import path
from . import views
urlpatterns = [
    path("test_chat_ws",views.test_chat_ws),
    path("ReadDepartments/<int:workspace_id>",views.read_categories),
    # path("get_fcm_token",views.get_fcm_token),

]
