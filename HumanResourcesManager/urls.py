from django.urls import path
from . import views
urlpatterns=[
    path("FolderManager",views.FolderManager.as_view()),
    path("FolderManager/<str:slug>", views.FolderManager.as_view()),
    path("GetFolderMembers", views.get_folder_members),
    path("EmployeeRequestManager/<str:slug>", views.EmployeeRequestManager.as_view()),
    path("EmployeeRequestManager", views.EmployeeRequestManager.as_view()),

]