from django.db import models
from UserManager.models import UserAccount
from extensions.utils import costum_date
from core.models import MainFile
from WorkSpaceManager.models import WorkSpace
import jdatetime
import os
from dotenv import load_dotenv
load_dotenv()
class Department(models.Model):
    title = models.CharField(max_length=55,null=True)
    color_code = models.CharField(max_length=55,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    
    members = models.ManyToManyField(UserAccount,related_name="departments")



class AnonCustomer(models.Model):

    fullname =models.CharField(max_length=50,null=True)
    phone_number = models.CharField(max_length=27,null=True,unique=True)
    created = models.DateField(auto_now_add=True)

    def persian_data (self):
        return costum_date(self.created)




class GroupRoom(models.Model):
    anon_customer = models.ForeignKey(AnonCustomer,on_delete=models.SET_NULL,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    status = models.BooleanField(default=False)

class Room(models.Model):

    TYPE_STATUS = (
        ("WAITING","waiting"),
        ("CLOSED","closed"),
        ("CONFIRMED","confirmed")
    )
    group = models.ForeignKey(GroupRoom,on_delete=models.CASCADE,null=True)
    department =models.ForeignKey(Department,on_delete=models.SET_NULL,null=True)
    room_status = models.CharField(max_length=30,choices=TYPE_STATUS,null=True)
    user_owner = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,related_name="chat_rooms",null=True)
    created = models.DateField(auto_now_add=True,null=True)
    anon_customer = models.ForeignKey(AnonCustomer,on_delete=models.CASCADE,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    activated = models.BooleanField(default=False)



class RoomMessage(models.Model):
    TYPE_STATUS = (
        ("anonymous","ANONYMOUS"),
        ("operator","OPERATOR"),
    )
    file = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="file_message")
    voice = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="voice_message")
    image = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="image_message")
    message_type = models.CharField(max_length=40,choices=TYPE_STATUS,null=True)
    room = models.ForeignKey(Room,on_delete=models.CASCADE,null=True,related_name="messages")
    body = models.TextField(null=True)
    file = models.FileField(upload_to="images/roommessages/")
    operator = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,null=True,blank=True)
    anonymous_user = models.ForeignKey(AnonCustomer,on_delete=models.SET_NULL,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    reply = models.ForeignKey("self",on_delete=models.CASCADE,null=True,blank=True)
    read_status = models.BooleanField(default=False)
    def fils_urls(self):
        base_url = os.getenv("BASE_URL")
        dic ={
            "voice_url":None,
            "file_url":None,
            "image_url":None,
        }
        try:
            if self.voice:
                dic["voice_url"]=f"{base_url}{self.voice.file.url}"
        except:
            pass
        try:
            if self.file:
                dic["file_url"]=f"{base_url}{self.file.file.url}"
        except:
            pass
        try:
            if self.image:
                dic["image_url"]=f"{base_url}{self.image.file.url}"
        except:pass
        return dic

    def jtime (self):
        
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)



        return jalali_datetime.strftime("%Y/%m/%d %H:%M:%S")

