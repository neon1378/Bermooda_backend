from random import choices

from django.db import models
from sqlalchemy import nulls_first
from core.models import  StudyCategory
# from CrmCore.models import *
from UserManager.models import UserAccount
from django.contrib.contenttypes.models import ContentType
# Create your models here.
import os
from dotenv import load_dotenv
load_dotenv()
from core.models import City,State,MainFile
from extensions.utils import costum_date
from core.models import SoftDeleteModel

class IndustrialActivity(SoftDeleteModel):
    title = models.CharField(max_length=150,null=True)
    refrence_id = models.IntegerField(default=0)




class WorkSpace (SoftDeleteModel):
    title = models.CharField(max_length=30,null=True,blank=True)
    owner = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True,related_name="workspace_owner",blank=True)
    is_authenticated = models.BooleanField(default=False)
    activated = models.BooleanField(default=True)


    BUSINESS_TYPE = (
        ("کسب کار آنلاین","کسب کار آنلاین "),
        ("کسب کار آفلاین","کسب کار آفلاین "),
        ("هر دو","هر دو")
    )
    PERSONAL_TYPE = (
        ("person","PERSON"),
        ("legal","LEGAL"),

    )
    PAYMENT_METHOD= (
        ("WALLET","wallet"),
        ("PLAN","plan"),
    )

    PLAN_METHOD=(
        ("startup","STARTUP"),
        ("launching","LUNCHING"),
        ("growth","GROWTH"),
        ("professional","PROFESSIONAL"),
    )


    plan_started_date = models.DateTimeField(null=True)
    payment_method = models.CharField(max_length=30,choices=PAYMENT_METHOD,default="wallet")
    plan_method = models.CharField(null=True,max_length=30,choices=PLAN_METHOD)
    company_name = models.CharField(max_length=55, null=True)
    person_type = models.CharField(max_length=6,choices=PERSONAL_TYPE,null=True)
    jadoo_workspace_id = models.PositiveBigIntegerField(default=0)
    business_type=models.CharField(max_length=50, choices=BUSINESS_TYPE,null=True)
    business_employer  = models.CharField(max_length=30,null=True,blank=True)

    reference_sub_category = models.PositiveBigIntegerField(default=0)
    reference_category = models.PositiveBigIntegerField(default=0)
    industrialactivity = models.ForeignKey(IndustrialActivity,on_delete=models.SET_NULL,null=True)
    jadoo_brand_name = models.CharField(max_length=100,null=True)
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)

    business_detail = models.TextField(null=True)
    city = models.ForeignKey(City,on_delete=models.SET_NULL,null=True)
    state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True)
    is_active = models.BooleanField(default=True)
    is_team_bonos = models.BooleanField(default=False)
    personal_information_status= models.BooleanField(default=False)

    national_card_image = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="national_image")
    document_image = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="duc_image")


    national_code = models.CharField(max_length=11,null=True)
    email = models.EmailField(null=True)
    postal_code = models.CharField(max_length=11,null=True)
    bank_number = models.CharField(max_length=24,null=True)
    phone_number= models.CharField(max_length=11,null=True)


    # Legal Fields
    tel_number = models.CharField(max_length=13,null=True)
    fax_number = models.CharField(max_length=20,null=True)
    economic_number = models.CharField(max_length=14,null=True)
    address = models.TextField(null=True)



    def wallet_balance(self):
        return self.wallet.balance



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

class WorkSpacePermission(SoftDeleteModel):
        PERMISSION_TYPE = (
            ("project_board","PROJECT_BOARD"),
            ("crm","CRM"),
            ("marketing_status","MARKETING_STATUS"),
            ("group_chat","GROUP_CHAT"),
            ("letters","LETTERS"),
            ("planing","PLANING"),
            ("marketing","MARKETING")
        )



        permission_type = models.CharField(max_length=50,null=True)
        is_active = models.BooleanField(default=True)

        workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="permissions")


class Link(SoftDeleteModel):
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="links")

    url = models.URLField(null=True)
class WorkspaceMember(SoftDeleteModel):


    GENDER = (
        ("male","MALE"),
        ("female","FEMALE")
    )




    MILITARY_STATUS = (
        ("subject_to_service","Subject To Service"),
        ("exempt_from_service", "Exempt From Service"),

        ("end_of_service", "End Of Service"),
        ("in_the_service", "In The Service"),

    )
    EXEMPT_TYPE = (
        ("medicine","MEDICINE"),
        ("sponsorship", "SPONSORSHIP"),
        ("education", "EDUCATION"),
        ("sacrifice", "SACRIFICE"),



    )



    INSURANCE_TYPE = (
        ("tamin_ejtemaei","Tamin Ejtemaei"),
        ("takmili","Takmili"),
        ("bazneshastegi","Bazneshastegi"),

        ("darmani", "Darmani"),
        ("hekmat", "Hekmat"),
        ("nobat", "Nobat"),
        ("other", "Other"),

    )


    EDUCATION_TYPE= (
        ("highschool","HIGHSCHOOL"),
        ("associate", "ASSOCIATE"),

        ("bachelor", "BACHELOR"),
        ("master", "MASTER"),

        ("phd", "PHD"),

    )



    insurance_type = models.CharField(max_length=15,null=True,blank=True,choices=INSURANCE_TYPE)
    military_status = models.CharField(choices=MILITARY_STATUS,max_length=30,null=True,blank=True)
    exempt_type = models.CharField(choices=EXEMPT_TYPE,max_length=30,null=True,blank=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="workspace_member")
    user_account = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True,related_name="user_member")
    fullname=models.CharField(max_length=200,null=True)
    first_name = models.CharField(max_length=70,null=True)
    last_name = models.CharField(max_length=70,null=True)
    jadoo_member_id = models.BigIntegerField(default=0)

    created = models.DateField(auto_now_add=True,null=True)
    is_accepted = models.BooleanField(default=True)
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="member_avatar")

    more_information = models.BooleanField(default=False)
    employee_code = models.CharField(max_length=20,null=True,blank=True)
    phone_number= models.CharField(max_length=11,null=True)
    email = models.EmailField(null=True,blank=True)
    date_of_birth = models.DateTimeField(null=True,blank=True)
    national_code = models.CharField(max_length=10,null=True,blank=True)
    certificate_number = models.CharField(max_length=10,null=True,blank=True)
    gender = models.CharField(max_length=10,choices=GENDER,null=True)
    state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True)
    city = models.ForeignKey(City,on_delete=models.SET_NULL,null=True)
    address = models.TextField(null=True,blank=True)
    postal_code = models.CharField(max_length=10,null=True,blank=True)
    marriage = models.BooleanField(default=False)
    number_of_children = models.IntegerField(default=0,blank=True)
    shaba_number = models.CharField(max_length=40,null=True,blank=True)
    date_of_start_to_work = models.DateTimeField(null=True,blank=True)
    contract_end_date = models.DateTimeField(null=True,blank=True)
    phone_number_static = models.CharField(max_length=15,null=True,blank=True)

    bad_record = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="member_bad_record")


    insurance_status = models.BooleanField(default=False)
    education_type = models.CharField(max_length=55,null=True,blank=True,choices=EDUCATION_TYPE)
    study_category = models.ForeignKey(StudyCategory,on_delete=models.SET_NULL,null=True)
    job_position = models.CharField(max_length=40,null=True,blank=True)
    is_emergency_information  = models.BooleanField(default=False)
    emergency_first_name =models.CharField(max_length=20,null=True ,blank=True)
    emergency_last_name = models.CharField(max_length=20,null=True ,blank=True)
    emergency_phone_number = models.CharField(max_length=12,null=True ,blank=True)
    emergency_relationship = models.CharField(max_length=30,null=True ,blank=True)



    def is_team_bonos_status(self):
        return self.workspace.is_team_bonos

    def jtime (self):
        return costum_date(self.created)

    def avatar_url (self):
        try:
            base_url = os.getenv("BASE_URL")
            return f"{base_url}{self.avatar.file.url}"
        except:
            return ""

    def permission_list(self):

        if self.user_account != self.workspace.owner:
            data = []
            for permission in  self.permissions.all():
                data.append(
                    {
                        "id":permission.id,
                        "permission_name":permission.permission_name,
                        "permission_type":permission.permission_type,
                    }
                )
            return data
        else:
            data=[
                {
                    "id": 1,
                    "permission_name": "project board",
                    "permission_type": "manager",
                },
                {
                    "id": 1,
                    "permission_name": "crm",
                    "permission_type": "manager",
                },
                {
                    "id":1,
                    "permission_name": "human_resources",
                    "permission_type": "manager",
                }
            ]
            return data


class MemberPermission (SoftDeleteModel):
    PERMISSION_TYPE =(
        ("manager","MANAGER"),
        ("expert","EXPERT"),
        ("no access","NO ACCESS"),


    )
    permission_name= models.CharField(max_length=70,null=True)
    member = models.ForeignKey(WorkspaceMember,on_delete=models.CASCADE,null=True,related_name="permissions")
    permission_type = models.CharField(max_length=60,choices=PERMISSION_TYPE,default="no access")

class ViewName(SoftDeleteModel):
    permission = models.ForeignKey(MemberPermission,on_delete=models.CASCADE,null=True,related_name="view_names")
    view_name = models.CharField(max_length=200,null=True)
    
class MethodPermission(SoftDeleteModel):
    METHOD_TYPE= (
        ("get","GET"),
        ("post","POST"),
        ("delete","DELETE"),
        ("put","PUT"),
        
    )
    view = models.ForeignKey(ViewName,on_delete=models.CASCADE,null=True,related_name="methods")
    method_name = models.CharField(max_length=55,choices=METHOD_TYPE,null=True)
    is_permission = models.BooleanField(default=False)


