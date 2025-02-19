from django.urls import path
from . import views
urlpatterns = [
    path("PlaningManager",views.PlaningManager.as_view()),
    path("PlaningManager/<int:plan_id>",views.PlaningManager.as_view()),
    path("AcceptOrDenyPlan",views.accept_or_deny_plan),
    
]
