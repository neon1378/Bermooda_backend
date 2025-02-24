from core.models import  SoftDeleteModel
from django.db import models
from UserManager.models import  UserAccount
from WorkSpaceManager.models import  WorkSpace,WorkspaceMember

# Create your models here.
class GroupMessage(SoftDeleteModel):
    workspace= models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    members = models.ManyToManyField(UserAccount,related_name="group_messages")


class TextMessage(SoftDeleteModel):
    text = models.TextField(null=True)
    owner = models.ForeignKey(UserAccount,related_name="text_messages",on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    group = models.ForeignKey(GroupMessage,on_delete=models.CASCADE,related_name="group_text_messages",null=True)






