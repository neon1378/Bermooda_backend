from django.db import models
from WorkSpaceManager.models import WorkSpace
from UserManager.models import UserAccount
from core.models import MainFile,SoftDeleteModel
from core.widgets import create_reminder
from WorkSpaceManager.models import WorkSpace

class MeetingLabel(SoftDeleteModel):
    title = models.CharField(max_length=20,null=True)
    titleTr1= models.CharField(max_length=20,null=True)
    color_code = models.CharField(max_length=12,null=True)
    workspace= models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    icon = models.TextField(null=True,blank=True)
    key_name = models.CharField(max_length=30,null=True,blank=True)

# Create your models here.

class Meeting(SoftDeleteModel):
    REMEMBER_TYPE = (
        ("hour", "HOUR"),
        ("minute", "MINUTE"),
        ("day", "day"),

    )
    REAPED_TYPE = (
        ("weekly", "WEEKLY"),
        ("daily", "DAILY"),
        ("monthly", "MONTHLY"),
        ("no_repetition", "No Repetition"),

    )

    reaped_type = models.CharField(max_length=100, choices=REAPED_TYPE, null=True)
    label = models.ForeignKey(MeetingLabel,on_delete=models.SET_NULL,null=True)
    files = models.ManyToManyField(MainFile)

    date_to_start = models.DateTimeField(null=True,blank=True)

    title = models.CharField(max_length=200, null=True)
    remember_type = models.CharField(max_length=80, choices=REMEMBER_TYPE, null=True, blank=True)
    remember_number = models.IntegerField(default=0,null=True,blank=True)

    description = models.TextField(null=True, blank=True)
    more_information = models.BooleanField(default=False)
    link = models.CharField(max_length=500, null=True, blank=True)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    start_meeting_time = models.TimeField(null=True,blank=True)
    end_meeting_time = models.TimeField(null=True,blank=True)








class MeetingHashtag(SoftDeleteModel):
    name = models.CharField(max_length=70, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, related_name="meeting_hashtags")


class MeetingPhoneNumber(SoftDeleteModel):
    phone_number = models.CharField(max_length=100, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, related_name="meeting_phone_numbers")


class MeetingEmail(SoftDeleteModel):
    email = models.EmailField(null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, related_name="meeting_emails")

class MeetingMember(SoftDeleteModel):
    USER_TYPE = (
        ("owner","OWNER"),
        ("member","OWNER"),
    )
    user_type = models.CharField(max_length=12,choices=USER_TYPE,null=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name="members")
    activated = models.BooleanField(default=False)



