from django.urls import path
from . import views
urlpatterns = [
    path("end_payment",views.end_payment),
    path("start_payment",views.start_payment),
    path("TransActionWallet",views.trans_action_wallet),
    path("TransActionWallet/<int:trans_action_id>",views.trans_action_wallet),

    path("create_workspaces",views.create_workspaces),
    path("WalletDetail",views.wallet_detail),

    path("waiting_payment_page/<str:track_id>",views.waiting_payment_page),
    path("unsuccess_payment/<int:trans_action_id>",views.unsuccess_payment),
    path("success_payment/<int:trans_action_id>",views.success_payment),
    path("CheckDiscountCode", views.check_discount_code),
    path("create_discount_json", views.create_discount_json),


]