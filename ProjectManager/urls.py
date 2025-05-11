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

    path("MyTaskCheckList/<int:project_id>",views.my_task_checklist),

    path("ReferralTask/<int:task_id>",views.referral_task),

    path("TaskArchiveManager",views.TaskArchiveManager.as_view()),
    path("TaskArchiveManager/<int:task_id>",views.TaskArchiveManager.as_view()),
    path("CheckListArchive/<int:task_id>",views.check_list_archive),

    path("CompletedTasks",views.completed_tasks),

    path("MainCheckListManager/<int:check_list_id>", views.MainCheckListManager.as_view()),
    path("MainCheckListManager", views.MainCheckListManager.as_view()),

    path("MainTaskManager/<int:task_id>", views.MainTaskManager.as_view()),

    path("MainTaskManager", views.MainTaskManager.as_view()),
    path("CheckListTimerManager/<int:timer_id>", views.CheckListTimerManager.as_view()),



]
