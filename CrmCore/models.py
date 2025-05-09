from django.db import models

from core.models import MainFile
from UserManager.models import UserAccount
import jdatetime
import locale

from WorkSpaceManager.models import WorkSpace,IndustrialActivity
import uuid
from django.db.models import Max
import os 
from dotenv import load_dotenv
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
load_dotenv()
from core.models import SoftDeleteModel,City,State
from django.utils.formats import number_format
class CrmDepartment(SoftDeleteModel):
    title = models.CharField(max_length=200,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="crm_departments")
    manager= models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)


# Create your models here.
class Label (SoftDeleteModel):
    # workspace = models.ForeignKey(WorkSpace,null=True,on_delete=models.CASCADE,related_name="label_customer")
    title =models.CharField(max_length=50,null=True)
    order = models.IntegerField(blank=True,null=True)
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


    def summery_customers(self):
        return {
            "customer_count":self.customer_group.all().count(),
            "customer_is_not_followed":self.customer_group.filter(is_followed=False).count(),
            "customer_is_followed":self.customer_group.filter(is_followed=True).count(),

        }



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

class Category (SoftDeleteModel):
    workspace = models.ForeignKey(WorkSpace,null=True,on_delete=models.CASCADE,related_name="category_customer")
    title =models.CharField(max_length=50,null=True)
    group_crm = models.ForeignKey(GroupCrm,on_delete=models.CASCADE,null=True,related_name="categories")

    created = models.DateField(auto_now_add=True)
class CustomerUser(SoftDeleteModel):
    CONECTION_TYPE = (
        ("phone","PHONE"),
        ("email","EMAIL"),
    )
    STATUS_TYPE = [
        ("dont_followed", "Dont Followed"),
        ("follow_in_another_time", "Follow In Another Time"),
        ("successful_sell", "Successful Sell"),
    ]
    PERSONAL_TYPE = (
        ("حقیقی","حقیقی"),
        ("حقوقی","حقوقی")
    )
    GENDER = (
        ("male","MALE"),
        ("female","FEMALE"),

    )
    gender = models.CharField(max_length=12,choices=GENDER,null=True,blank=True)
    industrial_activity = models.ForeignKey(IndustrialActivity,on_delete=models.SET_NULL,null=True,blank=True)
    customer_status=  models.CharField(max_length=30,choices=STATUS_TYPE,null=True)
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,blank=True)
    personal_type = models.CharField(max_length=9, choices=PERSONAL_TYPE,null=True)
    conection_type = models.CharField(max_length=30,choices=CONECTION_TYPE,default="phone")
    link =models.URLField(null=True,blank=True)
    is_followed = models.BooleanField(default=False)
    group_crm = models.ForeignKey(GroupCrm,on_delete=models.CASCADE,null=True,related_name="customer_group")
    workspace = models.ForeignKey(WorkSpace,null=True,on_delete=models.CASCADE,related_name="customer")
    user_account = models.ForeignKey(UserAccount,null=True,blank=True,on_delete=models.CASCADE,related_name="customer_user_acc")
    label = models.ForeignKey(Label,on_delete=models.SET_NULL,null=True,related_name="customer_label")
    category =models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    report =models.ManyToManyField(Report,blank=True,related_name="customer_user")
    last_selling_invoice_id = models.IntegerField(default=0)
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
    main_date_time_to_remember =models.DateTimeField(null=True)

    fax = models.CharField(max_length=20,null=True,blank=True)
    manager_national_code = models.BigIntegerField(null=True,blank=True)
    economic_code = models.BigIntegerField(null=True,blank=True)
    manager_phone_number = models.BigIntegerField(null=True,blank=True)

    agent_status = models.BooleanField(default=False)

    agent_name = models.CharField(max_length=55,null=True,blank=True)
    agent_email_or_link = models.CharField(max_length=200,null=True,blank=True)
    agent_phone_number = models.CharField(max_length=15,null=True,blank=True)
    agent_position = models.CharField(max_length=100,null=True,blank=True)

    order =models.IntegerField(default=0,blank=True)

    def group_crm_id_main(self):
        try:
            return self.group_crm.id
        except:
            return None

    def date_time_formated(self):
        try:
            locale.setlocale(locale.LC_ALL, 'fa_IR')

            # Parse the input string into a jdatetime.datetime object
            jalali_date = jdatetime.datetime.strptime(self.date_time_to_remember, "%Y/%m/%d %H:%M")

            # Format the jdatetime.datetime object into the desired Persian format
            formatted_date_persian = jalali_date.strftime("%d %B %Y | %H:%M ")
            # formatted_date_persian = jalali_date.strftime("%H:%M %Y/%B/%d ")
            return  formatted_date_persian
        except:
            return  ""


    def datetime_to_remember_persian (self):
        try:

            jalali_date = jdatetime.datetime.fromgregorian(datetime=self.main_date_time_to_remember)
            return jalali_date.strftime('%Y/%m/%d %H:%M')
        except:
            return None

    def app_avatar_url(self):
        try:
            base_url = os.getenv("BASE_URL")
            return f"{base_url}{self.avatar.file.url}"
        except:
            return None

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



class CustomerDocument(SoftDeleteModel):
    group_crm = models.ForeignKey(GroupCrm,on_delete=models.CASCADE,null=True)
    exel_file = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)



class CustomerBank(SoftDeleteModel):
    is_local = models.BooleanField(default=True)

    document= models.ForeignKey(CustomerDocument,on_delete=models.CASCADE,null=True)
    phone_number = models.CharField(max_length=14,null=True)
    state= models.CharField(max_length=50,null=True,blank=True)
    city= models.CharField(max_length=50,null=True,blank=True)

    main_state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True)
    main_city =models.ForeignKey(City,on_delete=models.SET_NULL,null=True)

    static_phone_number = models.CharField(max_length=18,null=True)
    address =models.TextField(null=True)
    email = models.CharField(max_length=60,null=True)

    fullname_or_company_name = models.CharField(max_length=40,null=True)



class GroupCrmMessage(SoftDeleteModel):

    MESSAGE_TYPE= (
        ("text","TEXT"),
        ("notification","NOTIFICATION")

    )
    #new fields begin
    message_type = models.CharField(max_length=15,choices=MESSAGE_TYPE,null=True,default="text",blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL,null=True)
    object_id = models.PositiveIntegerField(null=True)
    related_object = GenericForeignKey('content_type','object_id')
    body = models.TextField(null=True,blank=True)
    group_crm = models.ForeignKey(GroupCrm,on_delete=models.ForeignKey,null=True,related_name="messages")

    file = models.ManyToManyField(MainFile,blank=True)
    replay = models.ForeignKey("self",on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)

    def created_at_persian(self):
        PERSIAN_MONTHS = [
            "",  # month numbers start at 1
            "فروردین", "اردیبهشت", "خرداد",
            "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]
        if self.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=self.created_at)
            day = jalali_date.day
            month = PERSIAN_MONTHS[jalali_date.month]
            year = jalali_date.year
            time = jalali_date.strftime("%H:%M")
            return f"{day} {month} {year} | {time}"

    def created_at_date_persian(self):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created_at)

        return jalali_datetime.strftime("%Y/%m/%d")