from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("CategoryManager/<int:category_id>",views.CategoryManager.as_view()),
    path("CategoryManager",views.CategoryManager.as_view()),

    path("LabelMangaer/<int:label_id>",views.LabelMangaer.as_view()),
    path("LabelMangaer",views.LabelMangaer.as_view()),



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
    path("CustomerUserView/<int:customer_id>", views.CustomerUserView.as_view()),
    path("CampaignManager", views.CampaignManager.as_view()),
    path("CampaignManager/<int:campaign_id>", views.CampaignManager.as_view()),
    path("CampaignShow/<uuid:uuid>", views.campaign_show),
    path("CampaignForm/<uuid:uuid>", views.submit_form),

    path("GetCampaignForm/<int:campaign_form_id>", views.get_campaign_form),
    path("GetCampaignForm", views.get_campaign_form),
    path("ReferralTheLead", views.referral_the_lead),

    path("ReferralCustomer/<int:customer_id>", views.referral_customer),

    path("CustomerArchive", views.CustomerArchive.as_view()),
    path("CustomerArchive/<int:customer_id>", views.CustomerArchive.as_view()),

    path("GetMyCustomers", views.my_customers),

    path("create_label_steps", views.create_label_steps),

    path("LabelStepManager", views.LabelStepManager.as_view()),
    path("LabelStepManager/<int:step_id>", views.LabelStepManager.as_view()),

    path("CustomerSuccessSells", views.customer_success_sells),


    path("CustomerDocumentManager", views.CustomerDocumentManager.as_view()),
    path("CustomerDocumentManager/<int:document_id>", views.CustomerDocumentManager.as_view()),

    path("CustomerBankManager", views.CustomerBankManager.as_view()),
    path("CustomerBankManager/<int:customer_b_id>", views.CustomerBankManager.as_view()),
    path("SendCustomerToTheBoard", views.send_a_customer_to_board),

    path("CustomerStatusManager/<int:customer_id>", views.CustomerStatusManager.as_view()),
    path("ReSellACustomer/<int:customer_id>", views.resell_a_customer),
    path("ChangeCustomerStep/<int:customer_id>", views.change_customer_step),


]




