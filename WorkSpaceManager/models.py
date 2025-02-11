from django.db import models


# from CrmCore.models import *
from UserManager.models import UserAccount
from django.contrib.contenttypes.models import ContentType
# Create your models here.
import os
from dotenv import load_dotenv
load_dotenv()
from core.models import City,State,MainFile
from extensions.utils import costum_date
class MainCategory(models.Model):
    reference_id = models.CharField(max_length=400,null=True)
    title =models.CharField(max_length=50)
    icon = models.URLField(null=True)
    status = models.IntegerField(null=True)
    isDisable = models.BooleanField(default=False)
    isMedia = models.BooleanField(default=False)


class SubCategory (models.Model):
    main_category = models.ForeignKey(MainCategory,on_delete=models.CASCADE,null=True,related_name="sub_category")
    reference_id = models.CharField(max_length=400,null=True)
    title=models.CharField(max_length=50)
    icon= models.CharField(max_length=200,null=True)
    isDisable =models.IntegerField(null=True)
    isMedia =models.IntegerField(null=True)
    status= models.IntegerField(null=True)

class WorkSpace (models.Model):
    title = models.CharField(max_length=100,null=True)
    owner = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True,related_name="workspace_owner",blank=True)
    is_authenticated = models.BooleanField(default=False)
    activated = models.BooleanField(default=True)
    BUSINESS_TYPE = (
        ("کسب کار آنلاین","کسب کار آنلاین "),
        ("کسب کار آفلاین","کسب کار آفلاین "),
        ("هر دو","هر دو")
    )
    
    main_category = models.ForeignKey(MainCategory,on_delete=models.SET_NULL ,null=True)
    sub_category = models.ForeignKey(SubCategory,on_delete=models.SET_NULL ,null=True)
    jadoo_workspace_id = models.PositiveBigIntegerField(default=0)
    business_type=models.CharField(max_length=50, choices=BUSINESS_TYPE,null=True)


    reference_sub_category = models.PositiveBigIntegerField(default=0)
    reference_category = models.PositiveBigIntegerField(default=0)
    
    jadoo_brand_name = models.CharField(max_length=100,null=True,unique=True)
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)

    business_detail = models.TextField(null=True)
    city = models.ForeignKey(City,on_delete=models.SET_NULL,null=True)
    state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True)
    is_active = models.BooleanField(default=True)
    def avatar_url (self):
        try:
            base_url = os.getenv("BASE_URL")
            return f"{base_url}{self.avatar.file.url}"
        except:
            return None
    def state_name (self): 
        try:
            return self.state.name
        except:
            return ""
    def city_name (self):
        try:
            return self.city.name
        except:
            return ""
    def main_category_data(self):
        try:
            return {
                "id":self.main_category.id,
                "title":self.main_category.title
            }
        except:
            return {}
    def sub_category_data(self):
        try:
            return {
                "id":self.sub_category.id,
                "title":self.sub_category.title
            }
        except:
            return {}
class Link(models.Model):
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="links")

    url = models.URLField(null=True)
class WorkspaceMember(models.Model):
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="workspace_member")
    user_account = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True,related_name="user_member")
    fullname=models.CharField(max_length=200,null=True)
    created = models.DateField(auto_now_add=True,null=True)
    is_accepted = models.BooleanField(default=True)
    def jtime (self):
        return costum_date(self.created)
    




class MemberPermission (models.Model):
    PERMISSION_TYPE =(
        ("manager","MANAGER"),
        ("expert","EXPERT"),
        ("no access","NO ACCESS"),


    )
    permission_name= models.CharField(max_length=70,null=True)
    member = models.ForeignKey(WorkspaceMember,on_delete=models.CASCADE,null=True,related_name="permissions")
    permission_type = models.CharField(max_length=60,choices=PERMISSION_TYPE,default="no access")

class ViewName(models.Model):
    permission = models.ForeignKey(MemberPermission,on_delete=models.CASCADE,null=True,related_name="view_names")
    view_name = models.CharField(max_length=200,null=True)
    
class MethodPermission(models.Model):
    METHOD_TYPE= (
        ("get","GET"),
        ("post","POST"),
        ("delete","DELETE"),
        ("put","PUT"),
        
    )
    view = models.ForeignKey(ViewName,on_delete=models.CASCADE,null=True,related_name="methods")
    method_name = models.CharField(max_length=55,choices=METHOD_TYPE,null=True)
    is_permission = models.BooleanField(default=False)


