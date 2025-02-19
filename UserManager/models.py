from django.db import models
from django.contrib.auth.models import *
from extensions.utils import costum_date
from CustomerFinance.models import Invoice
from core.models import City,State,MainFile
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import User, Group
import os 
from dotenv import load_dotenv
load_dotenv()
class UserAccountManager(BaseUserManager):
    def create_user(self,username,password):
        if not username:
            raise ValueError("enter all fieldes")

        else:
            user = self.model(username=username,password=password)
            

            user.set_password(password)
            user.save()


            return user



    def create_superuser(self,username,password ):

        user = self.create_user(username=username,password=password)
    
        user.password = password
        password = password
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.set_password(password)
        user.save()
        return user

# Choice for Personal Type
class ReadyText (models.Model):
    text = models.TextField(null=True)

    owner = models.ForeignKey('UserAccount',on_delete=models.CASCADE,null=True)
    workspace = models.ForeignKey('WorkSpaceManager.WorkSpace',on_delete=models.CASCADE,null=True)

class UserAccount(AbstractBaseUser,PermissionsMixin):
    PERSONAL_TYPE = (
        ("حقیقی","حقیقی"),
        ("حقوقی","حقوقی")
    )

    personal_type = models.CharField(max_length=9, choices=PERSONAL_TYPE)

    # both
    national_code =models.BigIntegerField(null=True)
    phone_number = models.CharField(max_length=20,null=True,unique=True)
    email = models.EmailField(null=True)    

    # haghighi
    fullname = models.CharField(max_length=22,null=True)

    
    # hoghogh
    brand_name = models.CharField(max_length=100,null=True)
    economic_code = models.BigIntegerField(null=True)

    avatar = models.ForeignKey(MainFile,on_delete=models.CASCADE,null=True)
    username = models.CharField(max_length=70, unique=True,null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    fake_name = models.CharField(max_length=55,null=True)
    is_bonos = models.BooleanField(default=True)
    is_active = models.BooleanField(default =True)
    is_admin = models.BooleanField(default =True)
    is_staff = models.BooleanField(default =True)
    created = models.DateField(auto_now_add=True)
    expire_verify_code = models.TimeField(null=True)
    verify_code = models.CharField(max_length=10,null=True)
    USERNAME_FIELD = 'username'
    is_super_manager = models.BooleanField(default=False)
    ready_text = models.ManyToManyField(ReadyText)

    is_register = models.BooleanField(default=False)
    phone_incripted = models.TextField(null=True)
    current_ip_address = models.CharField(max_length=70,null=True)
    refrence_id = models.PositiveBigIntegerField(default=0)
    refrence_token = models.TextField(null=True)
    is_profile = models.BooleanField(default=False)
    current_workspace_id = models.PositiveBigIntegerField(default=0)

    is_auth = models.BooleanField(default=False)
    




    objects = UserAccountManager()

    def __str__(self):
        if self.phone_number == "09360604115":

            return f"{self.username} {self.id} this "
        else:
            return f"{self.username} {self.phone_number}"

    def has_module_perms(self,app_label):
        return True

    def full_name (self):
        try :
            return f"{self.fullname} "
        except:
            return " "

    def city_name (self):
        try:
            return self.city.name
        except:
            return None
    def state_name (self):
        try:
            return self.state.name
        except:
            return None
    def has_perm (self,perm,obj=None):
        return True

    def avatar_url (self):
        try:
            base_url = os.getenv("BASE_URL")
            return f"{base_url}{self.avatar.file.url}"
        except:
            return ""
    def avatar_url_main (self):
        try:
            base_url = os.getenv("BASE_URL")
            return {
                "id":self.avatar.id,
                "url":f"{base_url}{self.avatar.file.url}"
            }
        except:
            return {}
    def is_expired(self):
        from datetime import datetime
        now = datetime.now().time()
        return (datetime.combine(datetime.today(), now) - 
                datetime.combine(datetime.today(), self.expire_verify_code)) > timedelta(minutes=2)
    def jtime (self):
        return costum_date(self.created)

class BonosPhone(models.Model):
    phone = models.CharField(max_length=60,null=True)

class FcmToken(models.Model):
    token = models.TextField(null=True)
    user_account = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True,related_name="fcm_tokens")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Filter (models.Model):
    title = models.CharField(max_length=55,null=True)



class FilterTitle(models.Model):
    title = models.CharField(max_length=55,null=True)
    filter = models.ManyToManyField(Filter)

    
class GroupMain (models.Model):
    real_group_obj = models.OneToOneField(Group,on_delete=models.CASCADE)
    name= models.CharField(max_length=25)
    def __str__ (self):
        return self.name
class PermissionCategory(models.Model):
    real_name = models.CharField(max_length=100,null=True)
    name = models.CharField(max_length=55,null=True)
    workspace = models.PositiveBigIntegerField(null=True,blank=True)
    group_obj = models.ManyToManyField(GroupMain)
    def __str__(self):
        return self.name
class ViewName(models.Model):
    name = models.CharField(max_length=55,null=True)
    perm_category= models.ForeignKey(PermissionCategory,on_delete=models.CASCADE,null=True,related_name="view_names")
    nessery_manager = models.BooleanField(default=False)
  

    def __str__(self):
        return self.name
class PermissionType(models.Model):
    group_obj =models.OneToOneField(GroupMain,on_delete=models.CASCADE,related_name="gp_perm_type")
    PERMISSION_TYPE = (
        ("read","READ"),
        ("edit","EDIT"),
        ("manager","MANAGER"),
        ("notaccses","NOTACCSES"),

        

    )
    permission_type = models.CharField(max_length=40,choices=PERMISSION_TYPE,null=True)

    def __str__(self):
        return  f"{self.permission_type}  {self.group_obj.name} {self.id}"


class JadooToken(models.Model):
    token = models.TextField()



    

    



