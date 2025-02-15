
from dotenv import load_dotenv
import os 
from CrmCore.models import CustomerUser
from WorkSpaceManager.models import WorkSpace,WorkspaceMember
from datetime import datetime 
import requests
from django.utils.timezone import make_aware
import jdatetime
import json
from django.utils import timezone
from datetime import timedelta
from core.models import MainFile
from Notification.views import create_notification
from celery import shared_task
from .models import Wallet,WalletTransAction
from core.views import send_sms_core
import random
load_dotenv()


# 
# 

@shared_task
def decrease_wallet():
    print("fuck yes")
    send_sms_core("امین اله قلی", "09388148998")
    # Fetch all wallets and required environment variables
    # wallets = Wallet.objects.all()
    # price_per_mb = int(os.getenv("PRICE_FOR_ANY_MB", 0))  # Default to 0 if not set
    # price_per_user = int(os.getenv("PRICE_FOR_ANY_USER", 0))  # Default to 0 if not set
    #
    # for wallet in wallets:
    #     if not wallet.workspace.is_active:
    #         continue  # Skip inactive workspaces
    #
    #     # Calculate total MB used by the workspace
    #     mb_used = sum(
    #         file.file.size / (1024 * 1024)  # Convert bytes to MB
    #         for file in MainFile.objects.filter(its_blong=True, workspace_id=wallet.workspace.id)
    #         if file.file  # Ensure the file exists
    #     )
    #
    #     # Calculate total users in the workspace
    #     user_member_count = wallet.workspace.workspace_member.count()
    #
    #     # Calculate the total price to deduct
    #     decrease_price = (mb_used * price_per_mb) + (user_member_count * price_per_user)
    #
    #     if decrease_price > 0:
    #         # Deduct the price from the wallet balance
    #         wallet.balance -= decrease_price
    #         wallet.save()
    #
    #         # Create a wallet transaction record
    #         WalletTransAction.objects.create(
    #             wallet=wallet,
    #             price=decrease_price,
    #             trans_action_status="decrease",
    #             total_gb=mb_used,
    #             total_user=user_member_count,
    #             status_deposit=True,
    #             order_id=f"D_{random.randint(9999, 100000)}"
    #         )
    #
    #     # Deactivate workspace if balance is negative
    #     if wallet.balance < 0:
    #         wallet.workspace.is_active = False
    #         wallet.workspace.save()
    #
    #     # Send SMS if balance will be low tomorrow
    #     tomorrow_balance = wallet.balance - decrease_price
    #     if tomorrow_balance <= 50000:
    #         send_sms_core(wallet.workspace.owner.fullname, wallet.workspace.owner.phone_number)
    return None