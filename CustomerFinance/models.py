from django.db import models
from dotenv import load_dotenv
from django.utils import timezone
from extensions.utils import costum_date
import os
from datetime import datetime
from core.serializers import MainFileSerializer
from core.models import City,State,MainFile,SoftDeleteModel
import uuid
from core.widgets import persian_to_gregorian,gregorian_to_persian
from CrmCore.models import CustomerUser
load_dotenv()
from datetime import datetime, timedelta

class InvoiceStatus(SoftDeleteModel):
    group_crm = models.ForeignKey("CrmCore.GroupCrm",on_delete=models.CASCADE,null=True,related_name="invoice_statuses")
    title= models.CharField(max_length=30,null=True)
    color_code = models.CharField(max_length=30,null=True,blank=True)

class Information(SoftDeleteModel):

    fullname_or_company_name = models.CharField(max_length=50,null=True)
    email = models.EmailField(null=True,blank=True)
    address =models.TextField(null=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE,null=True,related_name="city_buyer")
    state = models.ForeignKey(State,on_delete=models.CASCADE,null=True,related_name="state_buyer")
    phone_number = models.CharField(max_length=40,null=True)

    def __str__(self):
        return f"{self.id}"
    def city_name (self):
        return self.city.name
    def state_name (self):
        return self.state.name

class ProductInvoice(SoftDeleteModel):
    title = models.CharField(max_length=50,null=True)
    count = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="تومان",null=True)
    code = models.CharField(max_length=55,null=True)
    unit = models.CharField(max_length=25,null=True)
    def formated_price (self):
        formatted_value = "{:,}".format(int(self.price))

        return formatted_value


    class Meta:
        ordering = ['id']
    def __str__(self):
        return f"{self.id}"

    def total_price (self):
        try:
            return self.price * self.count
        except:
            return 0 
        


class Invoice(SoftDeleteModel):
    PAYMENT_TYPE = (
        ("cash","CASH"),
        ("installment","INSTALLMENT"),
    )
    INVOICE_TYPE = (
        ("preinvoice","PREINVOICE"),
        ("finalinvoice","FINALINVOICE")
    )
    invoice_type = models.CharField(choices=INVOICE_TYPE,null=True,max_length=20)
    payment_type = models.CharField(choices=PAYMENT_TYPE,null=True,default="cash",max_length=22)
    date_to_pay = models.DateField(null=True)
    date_payed = models.DateField(null=True)
    status = models.ForeignKey(InvoiceStatus,on_delete=models.SET_NULL,null=True)
    customer = models.ForeignKey(CustomerUser,on_delete=models.CASCADE,null=True)
    login_ip = models.GenericIPAddressField(null=True)
    date_time_to_login = models.DateTimeField(null=True)
    verify_code = models.CharField(max_length=6,null=True)
    title = models.CharField(max_length=60,null=True)
    seller_information = models.OneToOneField(Information,on_delete=models.CASCADE,null=True,related_name="information_seller")
    buyer_information = models.OneToOneField(Information,on_delete=models.CASCADE,null=True,related_name="information_buyer")
    product = models.ManyToManyField(ProductInvoice)
    description = models.TextField(null=True)
    signature_main = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="invoice_signature")
    signature_buyer = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="invoice_signature_seller")
    logo_main = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="invoice_logo")
    discount = models.PositiveIntegerField(default=0)
    taxes = models.PositiveIntegerField(default=0)
    created = models.DateField(auto_now_add=True)
    invoice_code = models.CharField(max_length=90,null=True)
    qr_code = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,blank=True)
    created_date = models.DateField(null=True,blank=True)

    validity_date = models.DateField(null=True,blank=True)
    main_id = models.UUIDField(unique=True,null=True,blank=True)
    installment_count = models.IntegerField(default=1)
    interest_percentage =models.PositiveIntegerField(default=0,blank=True)



    def is_expired(self):
        if not self.date_time_to_login:
            return True  # Consider expired if the value is missing

        current_time = datetime.now()  # Naive datetime
        login_time = self.date_time_to_login.replace(tzinfo=None)  # Convert to naive

        return current_time >= login_time + timedelta(hours=1)

    def save(self, *args, **kwargs):
        if not self.main_id:  # اگر مقدار نداشته باشد
            self.main_id = uuid.uuid4()  # مقدار یکتا تولید کن
        super().save(*args, **kwargs)  #
    def signature_url(self):
        base_url = os.getenv("BASE_URL")
        try:
            return {
                "id":self.signature_main.id,
                "url":f"{base_url}{self.signature_main.file.url}"
            }
        except:return {}

    def logo_url (self):
        base_url = os.getenv("BASE_URL")
        try :
            return {
                "id":self.logo_main.id,
                "url":f"{base_url}{self.logo_file.file.url}"

            }
        except:return {}


    def signature_buyer_url (self):
        base_url = os.getenv("BASE_URL")
        try :
            return {
                "id":self.signature_buyer.id,
                "url":f"{base_url}{self.signature_buyer.file.url}"

            }
        except:return {}
    def invoice_date (self):
        return costum_date(self.created)


    def is_over(self):

        try:
            if self.validity_date < datetime.now().date():
                return True
            return False
        except:
            return False

    def created_date_persian(self):

        try:
            return gregorian_to_persian(self.created_date)
        except:
            return None
    def validity_date_persian(self):

        try:
            return gregorian_to_persian(self.validity_date)
        except:
            return None
    def factor_price (self):
            factor_price = 0
            for product in self.product.all():
                total_price = product.total_price()
                factor_price+=total_price
            final_price = (int(factor_price) - (int(factor_price) *   int(self.discount) / 100 )) + (int(factor_price) * (int(self.taxes) / 100))
            discount_price = int(factor_price) *( self.discount / 100)



            taxes_price =int(factor_price) *  (self.taxes/100)
            return {
                "final_price":final_price,
                "formated_final_price":"{:,}".format(int(final_price)),

                "factor_price":factor_price,

                "formated_factor_price":"{:,}".format(int(factor_price)),

                "discount_price":discount_price,

                "formated_discount_price":"{:,}".format(int(discount_price)),

                "taxes_price":taxes_price,

                "formated_taxes_price":"{:,}".format(int(taxes_price)),
            }




class Installment(SoftDeleteModel):
    price = models.DecimalField(max_digits=20,blank=True, decimal_places=0, help_text="Price in Tomans")
    date_to_pay = models.DateField(null=True,blank=True)
    order =models.IntegerField(default=0)
    created = models.DateField(auto_now_add=True,blank=True)

    invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE,null=True,related_name="installments",blank=True)
    is_paid = models.BooleanField(default=False,blank=True)
    date_payed =models.DateTimeField(null=True,blank=True)
    document_of_payment= models.ManyToManyField(MainFile)
    is_delayed= models.BooleanField(default=False,blank=True)
    class Meta:
        ordering = ['date_to_pay']


    def days_passed (self):
        try:



            now = timezone.now()
            days_passed = (now - self.date_time_to_pay).days
            return days_passed
        except:
            return None

    def created_persian (self):
        try:
            return gregorian_to_persian(self.created)
        except:
            return None


    def date_to_pay_persian(self):
        try:
            return gregorian_to_persian(self.date_to_pay)
        except:
            return None




    def date_payed_persian(self):

        try:
            return gregorian_to_persian(self.date_payed)
        except:
            return None
