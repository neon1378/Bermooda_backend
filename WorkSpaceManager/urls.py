from django.urls import path
from . import views
urlpatterns = [
    path("WorkSpaceManager/<int:workspace_id>",views.WorkspaceManager.as_view()),  
    path("WorkSpaceManager",views.WorkspaceManager.as_view()),    

    path("GetSubCategory/<int:category_id>",views.get_sub_category),    
    path("WorkSpaceManager/PersonalInformation/<int:workspace_id>",views.update_workspace_personal_information),    
    path("create_category",views.create_category),    
    path("CreateWorkSpaceAvatar/<int:workspace_id>",views.create_workspace_image),    
    path("DeleteWorkSpace/Member/<int:member_id>",views.delete_workspace_member),    
    path("create_permissions",views.create_permissions),    
    
    path("PermissionManager",views.PermissionManager.as_view()),    
    path("PermissionManager/<int:permission_id>",views.PermissionManager.as_view()),    
    path("AcceptWorkspaceInvitation/<int:notification_id>",views.accept_workspace_invitation),    
    
    
]
