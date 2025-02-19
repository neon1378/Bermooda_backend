from django.db import models
from WorkSpaceManager.models import WorkSpace
from UserManager.models import UserAccount
from core.models import MainFile
# Create your models here.

class Planing(models.Model):
    REMEMBER_TYPE= (
        ("hour","HOUR"),
        ("minute","MINUTE"),
        ("day","day"),


        

    )
    files = models.ManyToManyField(MainFile)
    
    date_in_calender = models.CharField(max_length=200,null=True)
    label_title = models.CharField(max_length=70,null=True)
    label_color_code = models.CharField(max_length=70,null=True)
    title = models.CharField(max_length=200,null=True)
    remember_date = models.CharField(max_length=200,null=True,blank=True)
    remember_type= models.CharField(max_length=80,choices=REMEMBER_TYPE,null=True,blank=True)
    reaped_status = models.BooleanField(default=False)
    description = models.TextField(null=True,blank=True)
    more_information = models.BooleanField(default=False)
    date_to_start =  models.CharField(max_length=200,null=True,blank=True)
    date_to_end =  models.CharField(max_length=200,null=True,blank=True)
    link = models.CharField(max_length=500,null=True,blank=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    range_date = models.ForeignKey('RangeDateCalender',on_delete=models.SET_NULL,null=True,related_name="range_date_calenders")

    def reaped_type_current(self):
        if self.range_date:
            return self.range_date.reaped_type
        else:
            return ""

class Hashtag (models.Model):
    name = models.CharField(max_length=70,null=True)
    planing = models.ForeignKey(Planing,on_delete=models.CASCADE,null=True,related_name="hashtags")
class PhoneNumber (models.Model):
    phone_number = models.CharField(max_length=100,null=True)
    planing = models.ForeignKey(Planing,on_delete=models.CASCADE,null=True,related_name="phone_numbers")
class Email (models.Model):
    email = models.EmailField(null=True)
    planing = models.ForeignKey(Planing,on_delete=models.CASCADE,null=True,related_name="emails")
class RangeDateCalender(models.Model):
    REAPED_TYPE= (
        ("weekly","WEEKLY"),
        ("daily","DAILY"),
        ("monthly","MONTHLY"),
        ("no_repetition","NO_REPETITION"),

        

    )
    start_date= models.CharField(max_length=200,null=True)
    reaped_type= models.CharField(max_length=100,choices=REAPED_TYPE,null=True)
    


class InvitedUser(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,null=True)
    planing = models.ForeignKey(Planing,on_delete=models.SET_NULL,null=True,related_name="invited_users")
    activated = models.BooleanField(default=False)

    
        
    


class ReminderPlanTime(models.Model):
    plan = models.ForeignKey(Planing,on_delete=models.CASCADE,null=True)
    date_time =models.CharField(max_length=100,null=True)
    