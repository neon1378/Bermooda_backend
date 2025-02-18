
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from django.views.generic import TemplateView
# from rest_framework_simplejwt import views as jwt_views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [

    path('manager/admin/user', admin.site.urls),
    path('v1/UserManager/',include("UserManager.urls")),
    path('v1/api-auth/', include('rest_framework.urls')),
    
    path('v1/MailManager/',include("MailManager.urls")),
    path('v1/ProjectManager/',include("ProjectManager.urls")),
    path('v1/CustomerFinance/',include("CustomerFinance.urls")),

    path('v1/CrmManager/',include("CrmCore.urls")),
    path('v1/SupportManager/',include("SupportManager.urls")),
    path('v1/WorkSpace/',include("WorkSpaceManager.urls")),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('v1/Core/',include("core.urls")),
    path('v1/Notification/',include("Notification.urls")),
    path('v1/WalletManager/',include("WalletManager.urls")),

    path('v1/Planing/',include("PlaningManager.urls")),


]
  

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)