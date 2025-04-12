from django.urls import path
from . import  views
urlpatterns = [
    path("Calender",views.CalenderManger.as_view()),
    path("MeetingLabelManager",views.MeetingLabelManager.as_view()),
    path("MeetingLabelManager/<int:label_id>",views.MeetingLabelManager.as_view()),

]