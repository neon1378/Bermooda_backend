from django.db import models
from dotenv import load_dotenv

from extensions.utils import costum_date
import os
from core.models import City,State,MainFile,SoftDeleteModel
import uuid

load_dotenv()

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
    payment_type = models.CharField(choices=PAYMENT_TYPE,null=True,default="cash",max_length=22)
    status = models.ForeignKey(InvoiceStatus,on_delete=models.SET_NULL,null=True)

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
    created_date = models.CharField(max_length=20,null=True)
    validity_date = models.CharField(max_length=20,null=True)
    main_id = models.UUIDField(unique=True,null=True,blank=True)
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
    

    def factor_price (self):
            factor_price = 0
            for product in self.product.all():
                total_price = product.total_price()
                factor_price+=total_price
            factor_price = (int(factor_price) - (int(factor_price) *   int(self.discount) / 100 )) + (int(factor_price) * (int(self.taxes) / 100))
            
            return factor_price
    
        
        




