
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

# @shared_task
# def create_reminder_line():


            


        
#     return ""