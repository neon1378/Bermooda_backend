from django.urls import path
from . import views 

urlpatterns = [
    path("UploadFile",views.upload_file),
    path("AppUpdateDetail",views.app_update_detail),

    

    
]
