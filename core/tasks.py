
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
from Notification.views import create_notification
from celery import shared_task
from django.utils import timezone
from .models import Reminder
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def delete_fake_files():
    one_day_ago = timezone.now() - timedelta(days=1)
    main_files = MainFile.objects.filter(its_blong=False)
    for file in main_files:
        if file.created <= one_day_ago:
            file.delete()
    return ""




@shared_task
def check_and_send_reminders():
    """Task to check for pending reminders and send them"""
    now = timezone.now()
    one_minute_ago = now - timedelta(minutes=1)

    pending_reminders = Reminder.objects.filter(
        remind_at__range=(one_minute_ago, now),

    )
    for reminder_obj in pending_reminders:
        class_name = reminder_obj.related_object.__class__.__name__

        if class_name == "CheckList":
            if not reminder_obj.related_object.status
                workspace = reminder_obj.related_object.task.project.workspace
                user = reminder_obj.related_object.responsible_for_doing
                create_notification(related_instance=reminder_obj.related_object, workspace=workspace, user=user,
                                    title=reminder_obj.title, sub_title=reminder_obj.sub_title, side_type="task_reminder")

            logger.info(f"Sent reminder to {user.fullname}")
        elif class_name == "CustomerUser":
            if not  reminder_obj.related_object.is_followed:
                workspace = reminder_obj.related_object.group_crm.workspace
                user = reminder_obj.related_object.user_account
                create_notification(related_instance=reminder_obj.related_object, workspace=workspace, user=user,
                                    title=reminder_obj.title, sub_title=reminder_obj.sub_title, side_type="customer_reminder")
                logger.info(f"Sent reminder to {user.fullname}")
