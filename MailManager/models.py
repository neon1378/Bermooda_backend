from django.db import models
from UserManager.models import UserAccount
from core.models import MainFile
import jdatetime
from extensions.utils import costum_date
from django.utils.text import slugify
from WorkSpaceManager.models import WorkSpace,WorkspaceMember
import random

# Create your models here.



class MailLabel(models.Model):
    title= models.CharField(max_length=70,null=True)
    color_code = models.CharField(max_length=80,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    


    
class MailStatus(models.Model):
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    
    title = models.CharField(max_length=200,null=True)





class Mail (models.Model):
    mail_image = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="mail_image_file",blank=True)
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    workspace =  models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=300,null=True)
    label = models.ForeignKey(MailLabel,on_delete=models.SET_NULL,null=True)
    members = models.ManyToManyField(UserAccount,related_name="mail_member")
    signature_status = models.BooleanField(default=False)
    mail_text = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    mail_code = models.CharField(max_length=200,null=True,unique=True,blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    files = models.ManyToManyField(MainFile,blank=True)
    status_mail = models.ForeignKey(MailStatus,on_delete=models.SET_NULL,null=True)



    def save(self, *args, **kwargs):
        if not self.mail_code:
            random_code = random.randint(9999,100000)
            self.mail_code = f"M_{random_code}"
        if not self.slug:
            random_code = random.randint(9999,100000)
            self.slug = slugify(f"mail{random_code}")
    
        
        super().save(*args, **kwargs)
    def create_mail_action (self,user_sender,user,title):
        new_mail_action = MailAction.objects.create(
            user_sender=user_sender,
            title=title,
            owner=user,
            mail_id=self.id
        )
    def __str__(self):
        return f"{self.title} {self.id}"
    def jtime(self):
        return costum_date(self.created)
    
    def sender_fullname(self):
        return self.creator.fullname
    def mail_type (self):
        return "داخلی"
    def sign_completed (self):
        status = True
        for sign in self.signatures.all():
            if sign.sign_status == False:
                status=False
                break
            else:
                continue
        return status

class FavoriteMail(models.Model):

    mail = models.ForeignKey(Mail,on_delete=models.CASCADE,null=True)
    status = models.BooleanField(default=False)
    user_account = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
class MailReport(models.Model):
    creator =models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    text = models.TextField(null=True)
    mail  = models.ForeignKey(Mail,on_delete=models.CASCADE,null=True,related_name="mail_reports")
    files = models.ManyToManyField(MainFile,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    def file_urls (self):
        urls = [url.file_url() for url in self.files.all()]
        
        return urls
    

    def __str__(self):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)


        return str(self.created)
    def jtime (self):
        
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)


        return jalali_datetime.strftime("%Y/%m/%d %H:%M")
class SignatureMail(models.Model):

    signature = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)
    sign_status =models.BooleanField(default=False)
    mail = models.ForeignKey(Mail,on_delete=models.CASCADE,null=True,related_name="signatures")
    owner = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    order= models.IntegerField(default=0)





class MailAction(models.Model):
    user_sender = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,null=True,related_name="mail_actionZ")
    title = models.CharField(max_length=300,null=True)
    color_code = models.CharField(max_length=300,null=True)
    mail = models.ForeignKey(Mail,on_delete=models.CASCADE,null=True,related_name="mail_actions")
    owner = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)



class CategoryDraft(models.Model):
    title = models.CharField(max_length=100,null=True)
    color_code = models.CharField(max_length=200,null=True)
    workspace= models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)

    owner = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)

class Draft (models.Model):
    draft_name = models.CharField(max_length=200,null=True)

    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True)
    owner = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=300,null=True)
    category = models.ForeignKey(CategoryDraft,on_delete=models.CASCADE)
    image = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="draft_image")
    label = models.ForeignKey(MailLabel,on_delete=models.SET_NULL,null=True)
    members =models.ManyToManyField(UserAccount,related_name="drafts")
    signature_status = models.BooleanField(default=False)
    text = models.TextField(null=True)
    files = models.ManyToManyField(MainFile,related_name="draft_files")