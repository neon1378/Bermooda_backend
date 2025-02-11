from django.urls import path
from . import views

urlpatterns = [
    path("InvoiceManager",views.InvoiceManager.as_view()),
    path("InvoiceManager/<int:invoice_id>",views.InvoiceManager.as_view()),    
        
]
