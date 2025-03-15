from core.models import  SoftDeleteModel
from django.db import models
from UserManager.models import  UserAccount
from WorkSpaceManager.models import  WorkSpace,WorkspaceMember
import jdatetime
import locale
# Create your models here.
class GroupMessage(SoftDeleteModel):
    workspace= models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    members = models.ManyToManyField(UserAccount,related_name="group_messages")

    def last_message (self):
        return self.group_text_messages.order_by("-created_at").first()
    def unread_messages(self,user_id):
        return self.group_text_messages.filter(owner_id=user_id,is_read=False).count()

class TextMessage(SoftDeleteModel):
    text = models.TextField(null=True)
    owner = models.ForeignKey(UserAccount,related_name="text_messages",on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    group = models.ForeignKey(GroupMessage,on_delete=models.CASCADE,related_name="group_text_messages",null=True)

    is_read = models.BooleanField(default=False)
    def jalali_time (self):
        # Convert Gregorian date to Jalali
        jalali_date = jdatetime.datetime.fromgregorian(date=self.created_at)

        # Extract only the time from `created_at`
        formatted_time_persian = jalali_date.strftime("%H:%M")

        return formatted_time_persian
    def jalali_date (self):
        locale.setlocale(locale.LC_ALL, 'fa_IR')
        jalali_date = jdatetime.datetime.fromgregorian(date=self.created_at)

        # Extract only the time from `created_at`
        formatted_time_persian = jalali_date.strftime("%d %B")

        return formatted_time_persian
