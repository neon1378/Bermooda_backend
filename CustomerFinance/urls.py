from django.urls import path
from . import views

urlpatterns = [
    path("InvoiceManager",views.InvoiceManager.as_view()),
    path("InvoiceManager/<int:invoice_id>",views.InvoiceManager.as_view()),

    path("InvoiceStatusManager",views.InvoiceStatusManager.as_view()),
    path("InvoiceStatusManager/<int:status_id>",views.InvoiceStatusManager.as_view()),
]
