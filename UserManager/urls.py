from django.urls import path
from . import views
app_name = "UserManager"

urlpatterns = [


    #User Registartion Url Begin 
    path("GetPhoneNumber",views.get_phone_number),
    path("VerifyPhoneNumber",views.verify_phone_number),
    path("CreateUsernamePasswords",views.create_username_pass),

    path("LoginUser",views.login_user),


    path("UserAccountManager",views.UserAccountManager.as_view()),
    path("UserAccountManager/<int:user_id>",views.UserAccountManager.as_view()),
    path("GetWorkSpaces",views.get_workspaces),
    


    #admin user api

    path("create_token",views.create_token,name="create_token"),
    # super user and admin user login url

    path("SuperuAdminu/Authentication",views.authuser,name="Authentication"),


    

    path("create_state_and_city",views.create_state_and_city,name="create_state_and_city"),

    path("get_all_state",views.get_all_state,name="get_all_state"),
    path("get_all_city_per_state/<int:state_id>",views.get_all_city_per_state,name="get_all_city_per_state"),
    #category customer api


    #register and login jado user leave them here for now just its a test



    path("GetCsrfToken",views.get_csrf_token,name="GetCsrfToken"),


    path("test_file",views.test_file,name="test_file"),
  

    

    #ReadyTextManager Begin 
    path("ReadyTextManager",views.ReadyTextManager.as_view()),
    path("ReadyTextManager/<int:ready_text_id>",views.ReadyTextManager.as_view()),
    #ReadyTextManager End 


    path("Register/GetPhoneNumber",views.get_phone_number),





    path("GetUserInfo",views.get_users_info),
    path("CreateWorkSpace",views.create_workspace),

    path("GetUserData",views.get_user_data),
    path("ChangeCurrentWorkspace",views.change_current_worksapce),
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('Change/Password', views.change_user_password, name='change_user_password'),

    path('Change/UserProfilePassword', views.change_user_profile_password, name='change_user_profile_password'),
    
    path("Change/Username",views.change_username),
    path("change_user",views.change_user),

    path("AddAvatarUser",views.add_user_avatar),
    path("Add/FcmToken",views.add_fcm_token),
    path("CreateAvatar",views.create_avatar),
    
    path("AccountVerify",views.account_verify),
    path("DeleteAccount",views.delete_account),

    

    
    


]
