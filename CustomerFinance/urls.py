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
]
