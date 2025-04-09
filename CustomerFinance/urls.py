from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
# router.register(r'InvoiceStatusManager', views.InvoiceStatusManager, basename='invoice-status')
urlpatterns = [
    path("InvoiceManager",views.InvoiceManager.as_view()),
    path("InvoiceManager/<int:invoice_id>",views.InvoiceManager.as_view()),
    # path('', include(router.urls)),
    path("InvoiceStatusManager",views.InvoiceStatusManager.as_view()),
    path("InvoiceStatusManager/<int:status_id>",views.InvoiceStatusDetailManager.as_view()),
    path("ChangeInvoiceStatus/<int:invoice_id>",views.change_invoice_status),
    path("InvoicePreview/<uuid:invoice_id>",views.invoice_preview),


    path("SendVerificationCode/<uuid:invoice_id>",views.send_verification_code),
    path("VerificationCode/<uuid:invoice_id>",views.verification_code),

    path("CreateBuyerSignature/<uuid:invoice_id>",views.create_buyer_signature),

    path("GetInvoiceCode",views.get_invoice_code),
    path("InstallMentView",views.InstallMentView.as_view()),
    path("InstallMentView/<int:installment_id>",views.InstallMentView.as_view()),



]
