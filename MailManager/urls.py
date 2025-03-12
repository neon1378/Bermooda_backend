from django.urls import path
from . import views
urlpatterns = [
    path ("Mail",views.MailManager.as_view()),
    path ("Mail/<int:mail_id>",views.MailManager.as_view()),
    path ("MailLabelManager",views.MailLabelManager.as_view()),
    path ("MailLabelManager/<int:label_id>",views.MailLabelManager.as_view()),
    path ("MailReportManager",views.MailReportManager.as_view()),
    path ("MailReportManager/<int:report_id>",views.MailReportManager.as_view()),
    path ("AddSignatureToMail/<int:recipient_id>",views.add_signature_to_mail),
    path ("MailStatusManager/<int:mail_id>",views.MailStatusManager.as_view()),
    path ("create_statuses",views.create_statuses),
    path ("AddOrDiscardToFavorite/<int:mail_id>",views.add_or_discard_to_favorite),
    
    path ("MailActions/<int:mail_id>",views.mail_actions),

    path ("DraftManger/Category",views.CategoryDraftManger.as_view()),
    path ("DraftManger/Category/<int:category_id>",views.CategoryDraftManger.as_view()),

    path ("DraftManger",views.DraftManger.as_view()),
    path ("DraftManger/<int:draft_id>",views.DraftManger.as_view()),



    # path ("MessageManager",views.MessageManager.as_view()),
    # path ("MessageManager/<int:conversation_id>",views.MessageManager.as_view()),

    # path ("GetAllUser",views.get_users),
]
