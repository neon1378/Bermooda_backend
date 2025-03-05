from django.db import models
from CustomerFinance.models import *
from core.models import MainFile
from UserManager.models import UserAccount
import jdatetime
from WorkSpaceManager.models import WorkSpace
import uuid
from django.db.models import Max
import os 
from dotenv import load_dotenv
load_dotenv()
from core.models import SoftDeleteModel
from django.utils.formats import number_format
class CrmDepartment(SoftDeleteModel):
    title = models.CharField(max_length=200,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="crm_departments")
    manager= models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)


# Create your models here.
class Label (SoftDeleteModel):
    # workspace = models.ForeignKey(WorkSpace,null=True,on_delete=models.CASCADE,related_name="label_customer")
    title =models.CharField(max_length=50,null=True)
    color= models.CharField(max_length=50,null=True)
    group_crm = models.ForeignKey("GroupCrm",on_delete=models.CASCADE,null=True,related_name="label_customer")

    created = models.DateField(auto_now_add=True)


class LabelStep(SoftDeleteModel):
    label = models.OneToOneField(Label,on_delete=models.CASCADE,null=True,related_name="label_step")
    created = models.DateTimeField(auto_now_add=True, null=True)

class Step(SoftDeleteModel):
    title =models.CharField(max_length=30,null=True)
    step = models.IntegerField(default=0,blank=True,null=True)
    label_step = models.ForeignKey(LabelStep,on_delete=models.CASCADE,null=True,related_name="steps")

    created = models.DateTimeField(auto_now_add=True, null=True)




class Category (SoftDeleteModel):
    workspace = models.ForeignKey(WorkSpace,null=True,on_delete=models.CASCADE,related_name="category_customer")
    title =models.CharField(max_length=50,null=True)

    created = models.DateField(auto_now_add=True)
class ActionData(SoftDeleteModel):
    CHOICE =(
        ("status","status"),
        ("invoice","invoice"),
        ("refrral","refrral"),

    )
    action_type = models.CharField(max_length=50,choices=CHOICE,null=True)
    object_id = models.IntegerField(default=0)
    user_author = models.IntegerField(default=0)
    user_reciver = models.IntegerField(default=0)
      
    before_status =models.CharField(max_length=40,null=True)
    current_status = models.CharField(max_length=50,null=True)

class Report(SoftDeleteModel):
    description = models.TextField(null=True)
    date_to_remember = models.CharField(max_length=30,null=True)
    time_to_remember = models.CharField(max_length=30,null=True)
    possibility_of_sale = models.CharField(max_length=30,null=True)     
    main_file = models.ManyToManyField(MainFile)
    report_type = models.BooleanField(default=False)
    action_data = models.OneToOneField(ActionData,on_delete=models.SET_NULL,null=True)
    invoice_id = models.PositiveBigIntegerField(default=0)
    label_id = models.PositiveBigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True,null=True)
    author = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,null=True)

    payment_status= models.BooleanField(default=False)
    payment_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="تومان",null=True,blank=True)
    notif_remember=models.BooleanField(default=False)
    notif_payment = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50,null=True)
    payment_time_to_remember=  models.CharField(max_length=30,null=True)
    payment_date_to_remember= models.CharField(max_length=30,null=True)
    payment_description = models.TextField(null=True)
    
    def jtime (self):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)


        return jalali_datetime.strftime("%Y/%m/%d %H:%M:%S") 

    def text_type (self):
        if self.report_type:

            if self.action_data.action_type == "status":
                before_label = Label.objects.get(id=self.action_data.before_status)
                current_label = Label.objects.get(id=self.action_data.current_status )

                return f"وضعیت {before_label.title} به {current_label.title } تغییر کرد"
            elif self.action_data.action_type == "refrral":
                from UserManager.models import UserAccount
                try:
                    user_author = UserAccount.objects.get(id=self.action_data.user_author)
                    user_reciver = UserAccount.objects.get(id=self.action_data.user_reciver)
                    return f"از {user_author.first_name}  {user_author.last_name} به {user_reciver.first_name} {user_reciver.last_name} ارچاع داده شد"
                except:
                    return ""
            elif self.action_data.action_type == "invoice":
                invoice_obj = Invoice.objects.get(id=self.action_data.object_id)
                return f"صورت حساب با کد {invoice_obj.invoice_code} ثبت شد "
        else:
            return self.description
    
    def get_params (self):
        list_text = []
        if self.invoice_id > 0:
            list_text.append({
                "type":"invoice",
                "text":"فاکتور رسمی ارسال شد"
            })
        if self.label_id > 0:
            try:
                label_obj = Label.objects.get(id= self.label_id)
                list_text.append({

                "type":"status",
                "text": f" وضعیت {label_obj.title}"
                })
            except:
                pass
        list_text.append({

                "type":"sell",
                "text": f" احتمال فروش {self.possibility_of_sale}"
            })
        if self.date_to_remember and self.time_to_remember:
            list_text.append({

                    "type":"reminder",
                    "text": f" زمان یاد آوری{self.date_to_remember}  {self.time_to_remember}"
                })
        return list_text
    def report_action (self):
        if self.report_type:
            if self.action_data.action_type == "invoice":
                return {
                    "type":"invoice",
                    "object_id":self.action_data.object_id
                }
            else:
                return {}
        return {}
    

class GroupCrm (SoftDeleteModel):
    workspace =models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="group_crm")
    manager= models.ForeignKey(UserAccount,on_delete=models.SET_NULL,null=True)
    title = models.CharField(max_length=200,null=True)
    members = models.ManyToManyField(UserAccount,related_name="group_crm_user")
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    department = models.ForeignKey(CrmDepartment,on_delete=models.CASCADE,null=True,related_name="group_crm")




    def profit_price(self):
        total_price =0
        for customer in self.customer_group.all():

            for report in customer.report.all():
                if report.payment_status:
                    try:
                        total_price+=report.payment_price
                    except:
                        pass
        return number_format(total_price, use_l10n=True)

    def user_count (self):
        return self.user_account.all().count()
    def avatar_url (self):
        try:
            base_url = os.getenv("BASE_URL")
            return f"{base_url}{self.avatar.file.url}"        
        except:
            return ""   


class CustomerUser(SoftDeleteModel):
    CONECTION_TYPE = (
        ("phone","PHONE"),
        ("email","EMAIL"),
    )
    PERSONAL_TYPE = (
        ("حقیقی","حقیقی"),
        ("حقوقی","حقوقی")
    )
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,blank=True)
    personal_type = models.CharField(max_length=9, choices=PERSONAL_TYPE,null=True)
    conection_type = models.CharField(max_length=30,choices=CONECTION_TYPE,default="phone")


    group_crm = models.ForeignKey(GroupCrm,on_delete=models.CASCADE,null=True,related_name="customer_group")
    workspace = models.ForeignKey(WorkSpace,null=True,on_delete=models.CASCADE,related_name="customer")
    user_account = models.ForeignKey(UserAccount,null=True,blank=True,on_delete=models.CASCADE,related_name="customer_user_acc")
    label = models.ForeignKey(Label,on_delete=models.SET_NULL,null=True,related_name="customer_label")
    category =models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    report =models.ManyToManyField(Report,blank=True,related_name="customer_user")
    invoice = models.ManyToManyField(Invoice,related_name="customer_invoice",blank=True)
    fullname_or_company_name = models.CharField(max_length=100,null=True)
    phone_number = models.CharField(max_length=40,null=True)
    phone_number_static = models.CharField(max_length=50,null=True,blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    address = models.TextField(null=True,blank=True) 
    email = models.EmailField(null=True,blank=True)
    website = models.CharField(max_length=200,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    legal_information =models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    possibility_of_sale = models.IntegerField(default=0)
    date_time_to_remember= models.CharField(max_length=100,null=True)


    fax = models.BigIntegerField(null=True,blank=True)
    manager_national_code = models.BigIntegerField(null=True,blank=True)
    economic_code = models.BigIntegerField(null=True,blank=True)
    manager_phone_number = models.BigIntegerField(null=True,blank=True)

    agent_status = models.BooleanField(default=False)

    agent_name = models.CharField(max_length=55,null=True,blank=True)
    agent_email_or_link = models.CharField(max_length=200,null=True,blank=True)
    agent_phone_number = models.CharField(max_length=15,null=True,blank=True)
    agent_position = models.CharField(max_length=100,null=True,blank=True)

    order =models.IntegerField(default=0,blank=True)
    def category_data (self):
        try:
            return  {
                "id":self.category.id,
                "title":self.category.title
            }
        except:
            return {}
    def avatar_url(self):
        try:
            base_url = os.getenv("BASE_URL")
            return {
                "id":self.avatar.id,
                "url":f"{base_url}{self.avatar.file.url}"
            }
        except:
            return {}


    def city_name(self):
        if self.city:  # Check if the city exists
            return self.city.name
        return None

    def state_name(self):
        if self.state:  # Check if the state exists
            return self.state.name
        return None
    def step_status(self):
        customer_step_objs = self.customer_step.filter(label=self.label)
        step_count  = 0
        if customer_step_objs.exists():
            step_list = []

            for step in customer_step_objs:
                if step.step is not None:
                    step_list.append({"id":step.id,"step":step.step})
            if step_list:
                max_step_obj = max(step_list, key=lambda x: x["step"].step)
                step_count= max_step_obj['step'].step
        return step_count




class CustomerStep(SoftDeleteModel):
    customer = models.ForeignKey(CustomerUser,on_delete=models.CASCADE,null=True,related_name="customer_step")
    label = models.ForeignKey(Label,on_delete=models.CASCADE,null=True)
    step= models.ForeignKey(Step,on_delete=models.CASCADE,null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)



class Campaign(SoftDeleteModel):
    image = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)
    group_crm = models.ForeignKey(GroupCrm,on_delete=models.CASCADE,null=True,related_name="campaigns")
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=300,null=True)
    description = models.TextField(null=True)

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True,null=True)




    def image_url(self):
        base_url =os.getenv("BASE_URL")
        try:
            return {
                "id":self.image.id,
                "url":f'{base_url}{self.image.file.url}'
            }
        except:
            return {}

    def jtime(self):

        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)

        return jalali_datetime.strftime("%Y/%m/%d %H:%M:%S")

class CampaignField(SoftDeleteModel):
    TYPE = (

        ("phone_number","PHONE_NUMBER"),
        ("text","TEXT"),
        ("number","NUMBER"),
        ("email","EMAIL"),
        ("link","LINK"),




    )
    title= models.CharField(max_length=70,null=True)

    field_type = models.CharField(max_length=60,choices=TYPE,null=True)
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE,null=True,related_name="fields")

class CampaignForm (SoftDeleteModel):
    fullname =  models.CharField(max_length=100,null=True)
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE,related_name="forms",null=True)



class CampaignFormData(SoftDeleteModel):
    TYPE = (

        ("phone_number","PHONE_NUMBER"),
        ("text","TEXT"),
        ("number","NUMBER"),
        ("email","EMAIL"),
        ("link","LINK"),




    )
    field_type = models.CharField(max_length=60, choices=TYPE, null=True)
    title = models.CharField(max_length=55,null=True)
    text = models.TextField(null=True)

    campaign_form =models.ForeignKey(CampaignForm,on_delete=models.CASCADE,null=True,related_name="form_data")


class IpExist(SoftDeleteModel):

    ip = models.GenericIPAddressField(null=True)
    campaign =  models.ForeignKey(Campaign,on_delete=models.CASCADE,null=True)


class IpAshol(SoftDeleteModel):
    ip = models.GenericIPAddressField(null=True)

