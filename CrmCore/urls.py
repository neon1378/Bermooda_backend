from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("CategoryManager/<int:category_id>",views.CategoryManager.as_view()),
    path("CategoryManager",views.CategoryManager.as_view()),

    path("LabelMangaer/<int:label_id>",views.LabelMangaer.as_view()),
    path("LabelMangaer",views.LabelMangaer.as_view()),


    path("CustomerUserManager",views.CustomerUserManager.as_view()),
    path("CustomerUserManager/<int:customer_id>",views.CustomerUserManager.as_view()),
    path("ReportManager/<int:report_id>",views.ReportManager.as_view()),
    path("ReportManager",views.ReportManager.as_view()),

    path("Change/CustomerSupervisor/<int:customer_id>",views.change_customer_supervisor),

    path("GroupCrmManager",views.GroupCrmManager.as_view()),
    path("GroupCrmManager/<int:group_id>",views.GroupCrmManager.as_view()),
    path("GroupCrmMembers/<int:group_id>",views.get_crm_group_members),
    path("CreateReportMessage/<int:customer_id>",views.create_report_message),

    path("Change/CustomerStatus/<int:customer_id>",views.change_customer_status),

    path("CrmDepartmentManager/<int:department_id>",views.CrmDepartmentManager.as_view()),
    path("CrmDepartmentManager",views.CrmDepartmentManager.as_view()),

    path("ExistMemberCrm/<int:group_id>",views.exist_member_in_crm),
    path("CustomerUserView", views.CustomerUserView.as_view()),
    path("CampaignManager", views.CampaignManager.as_view()),
    path("CampaignManager/<int:campaign_id>", views.CampaignManager.as_view()),
    path("CampaignShow/<uuid:uuid>", views.campaign_show),
    path("CampaignForm/<uuid:uuid>", views.submit_form),

    path("GetCampaignForm/<int:campaign_form_id>", views.get_campaign_form),

]


    

