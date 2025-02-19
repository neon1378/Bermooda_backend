from django.urls import path 
from . import views
urlpatterns = [
    path("ProjectManager",views.ProjectManager.as_view()),

    path("ProjectManager/<int:project_id>",views.ProjectManager.as_view()),
    path("GetProjectUser/<int:project_id>",views.get_project_users),


    path("TaskManager/<int:project_id>",views.TaskManager.as_view()),
    path("TaskManager",views.TaskManager.as_view()),

    # path("CheckListManager",views.CheckListManager.as_view()),
    path("CheckListManager/<int:checklist_id_or_task_id>",views.CheckListManager.as_view()),



    path("test_html_page/<int:project_id>",views.test_html_page),
    
    path("CategoryProjectManager",views.CategoryProjectManager.as_view()),
    path("CategoryProjectManager/<int:category_id>",views.CategoryProjectManager.as_view()),
    path("TaskReportManager/<int:report_id>",views.TaskReportManager.as_view()),
    path("TaskReportManager",views.TaskReportManager.as_view()),
    path("LabelTaskManager",views.LabelTaskManager.as_view()),
    path("LabelTaskManager/<int:label_id>",views.LabelTaskManager.as_view()),
    
    path("ProjectDepartmentManager",views.ProjectDepartmentManager.as_view()),
    path("ProjectDepartmentManager/<int:department_id>",views.ProjectDepartmentManager.as_view()),
    


    
]
