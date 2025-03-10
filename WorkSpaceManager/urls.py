from django.urls import path
from . import views
urlpatterns = [
    path("WorkSpaceManager/<int:workspace_id>",views.WorkspaceManager.as_view()),  
    path("WorkSpaceManager",views.WorkspaceManager.as_view()),    


    path("WorkSpaceManager/PersonalInformation/<int:workspace_id>",views.update_workspace_personal_information),    
    path("create_category",views.create_category),    
    path("CreateWorkSpaceAvatar/<int:workspace_id>",views.create_workspace_image),    
    path("DeleteWorkSpace/Member/<int:member_id>",views.delete_workspace_member),    
    path("create_permissions",views.create_permissions),    
    path("PermissionManager",views.PermissionManager.as_view()),
    path("PermissionManager/<int:permission_id>",views.PermissionManager.as_view()),
    # path("AcceptWorkspaceInvitation/<int:notification_id>",views.accept_workspace_invitation),
    path("AcceptWorkspaceInvitation", views.accept_workspace_invitation),
    path("GetManagerUser", views.get_manager_users),
    path("GetExpertUser", views.get_expert_users),
    path("GetIndustrialActivity",views.get_industrial_activity),
    path("WorkSpaceMemberManger",views.WorkSpaceMemberManger.as_view()),
    path("WorkSpaceMemberManger/<int:member_id>",views.WorkSpaceMemberManger.as_view()),

    path("WorkSpaceMemberArchive/<int:member_id>",views.WorkSpaceMemberArchive.as_view()),
    path("WorkSpaceMemberArchive",views.WorkSpaceMemberArchive.as_view()),

    path("GetTextInvite",views.get_text_workspace_invite),
    path("create_group_message",views.create_group_message),

    path("UpdateWorkSpaceInfo/<int:workspace_id>",views.update_workspace_information),
    path("WorkSpacePermissionManager/<int:permission_id>",views.WorkSpacePermissionManager.as_view()),
    path("WorkSpacePermissionManager",views.WorkSpacePermissionManager.as_view()),
    path("create_workspace_to_jadoo",views.create_workspace_to_jadoo),



]



