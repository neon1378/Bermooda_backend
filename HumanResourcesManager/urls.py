from django.urls import path
from . import views
urlpatterns=[
    path("FolderManager",views.FolderManager.as_view()),
    path("FolderManager/<str:slug>", views.FolderManager.as_view()),

]