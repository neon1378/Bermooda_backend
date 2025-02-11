
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
from .models import MainFile
from Notification.views import create_notification
from celery import shared_task
load_dotenv()


@shared_task
def delete_fake_files():
    one_day_ago = timezone.now() - timedelta(days=1)
    main_files = MainFile.objects.filter(its_blong=False)
    for file in main_files:
        if file.created <= one_day_ago:
            file.delete()
    return ""
