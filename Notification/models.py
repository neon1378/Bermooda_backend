from django.db import models
from WorkSpaceManager.models import WorkSpace
from UserManager.models import UserAccount
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.
import jdatetime

class Notification(models.Model):

    
    title = models.CharField(max_length=40,null=True)
    sub_title = models.CharField(max_length=200,null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL,null=True)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')

    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    user_account = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True,related_name="notifications")

    is_read = models.BooleanField(default=False)
    side_type= models.CharField(max_length=50,null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    

    def jtime (self):
        
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)



        return jalali_datetime.strftime("%Y/%m/%d %H:%M:%S")