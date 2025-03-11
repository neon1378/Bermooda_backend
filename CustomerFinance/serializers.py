from distutils.file_util import write_file
from datetime import timedelta
from django.utils import timezone
from celery.bin.worker import worker
from django.utils.text import normalize_newlines
from rest_framework.serializers import ModelSerializer
from .models import *
from core.serializers import MainFileSerializer
from rest_framework import serializers
from core.widgets import  persian_to_gregorian
from CrmCore.models import CustomerUser
from django.shortcuts import get_object_or_404
# SellerCopmany
# BuyerInformation
# Product
#Invoice
import random

from WorkSpaceManager.models import WorkSpace

class ProductInvoiceSerializer(ModelSerializer):
    class Meta:
        model =ProductInvoice
        fields = [
            "id",
            "title",
            "count",
            "price",
            "code",
            "unit",
        ]

class InformationSerializer(ModelSerializer):

    class Meta:
        model = Information
        fields = [
            "fullname_or_company_name",
            "email",
            "address",
            "city",
            "state",
            "phone_number",
            "city_name",
            "state_name",

        ]
    




class InvoiceStatusSerializer(ModelSerializer):
    group_crm_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = InvoiceStatus
        fields =[
            "id",
            "title",
            "color_code",
            "group_crm_id"
        ]

    def create(self, validated_data):
        new_invoice_status =InvoiceStatus.objects.create(**validated_data)
        return new_invoice_status
    def update(self, instance, validated_data):
        validated_data.pop("group_crm_id",None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class InstallMentSerializer(ModelSerializer):
    document_of_payment = MainFileSerializer(read_only=True)
    document_of_payment_id =serializers.IntegerField(write_only=True,required=False)

    class Meta:
        model = Installment
        fields =[
            "id",
            "price",
            "date_to_pay",
            "invoice",
            "is_paid",
            "date_payed",
            "is_delayed",
            "document_of_payment",
            "document_of_payment_id",
            "days_passed",
            "created_persian",
            "date_to_pay_persian",
            "date_payed_persian",
        ]










class InvoiceSerializer(ModelSerializer):
    qr_code = MainFileSerializer(read_only=True)

    installments = InstallMentSerializer(read_only=True,many=True)
    installment_period_day  = serializers.IntegerField(write_only=True,required=False)
    installment_price = serializers.IntegerField(write_only=True,required=False)
    seller_information = InformationSerializer(read_only=True)
    buyer_information = InformationSerializer(read_only=True)
    product= ProductInvoiceSerializer(many=True,read_only=True)
    workspace_id= serializers.IntegerField(read_only=True)
    signature_id =serializers.IntegerField(write_only=True,required=False)
    product_list= serializers.ListField(write_only=True,required=True)
    status = InvoiceStatusSerializer(read_only=True)
    status_id = serializers.IntegerField(write_only=True,required=False)
    seller_information_data =serializers.JSONField(write_only=True,required=True)
    signature_buyer_id = serializers.IntegerField(write_only=True,required=False)
    created_date = serializers.CharField(write_only=True,required=True)
    validity_date = serializers.CharField(write_only=True,required=True)
    class Meta:
        model = Invoice
        fields = [
            "status",
            "status_id",
            "qr_code",
            "id",
            "main_id",
            "signature_url",
            "signature_buyer_id",
            "logo_url",
            "payment_type",
            "seller_information",
            "buyer_information",
            "product",
            "created_date",
            "signature_buyer_url",
            "validity_date",
            "description",
            "discount",
            "taxes",
            "created",
            "invoice_code",
            "factor_price",
            "invoice_date",
            "workspace_id",
            "signature_id",
            "product_list",
            "installment_period_day",
            "installment_price",
            "installments",
            "seller_information_data",
            "installment_period_day",
            "installment_price",
      
        ]



    def create(self,validated_data):


        workspace_id =validated_data.pop("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        products = validated_data.pop("product_list",[])
        signature_id = validated_data.pop("signature_id",None)

        installment_period_day = validated_data.pop("installment_period_day",None)
        installment_price = validated_data.pop("installment_price",None)
        created_date = validated_data.pop("created_date",None)
        validity_date = validated_data.pop("validity_date",None)
        signature_buyer_id= validated_data.pop("signature_buyer_id",None)
        seller_information = validated_data.pop("seller_information_data")

        state_seller = seller_information.pop("state",None)
        city_seller = seller_information.pop("city",None)
        payment_type = validated_data.get("payment_type",None)
        if products == [] or products == None:
            raise serializers.ValidationError(
                {
                    "status":False,
                    "message":"انتخاب حداقل یک محصول اجباری میباشد"
                }
            )

        if not workspace_obj.personal_information_status:
            raise serializers.ValidationError({
                "status":False,
                "message":"not_information",
                "data":{},
            })

        seller_information_obj = Information(
            fullname_or_company_name =workspace_obj.jadoo_brand_name,
            email = workspace_obj.email,
            address = workspace_obj.address,
            city = workspace_obj.city,
            state = workspace_obj.state,
            phone_number = workspace_obj.phone_number,
        )
        seller_information_obj.save()

        buyer_information_obj = Information(
            
            **seller_information,

            
        )
        if state_seller:

            state= State.objects.get(id=state_seller)
            buyer_information_obj.state =state
        if city_seller:
            city= City.objects.get(id=city_seller)
            buyer_information_obj.city =city

        buyer_information_obj.save()
        new_invoice = Invoice(
            **validated_data,
            created_date = persian_to_gregorian(created_date),
            validity_date = persian_to_gregorian(validity_date),
            buyer_information=buyer_information_obj,
            seller_information=seller_information_obj,
            invoice_code = f"#{random.randint(1,100000)}",


        )


        if workspace_obj.avatar:
            new_invoice.logo_main= workspace_obj.avatar
        if signature_id:
            signature_file_main_file = MainFile.objects.get(id=signature_id)
            signature_file_main_file.its_blong=True
            signature_file_main_file.save()
            new_invoice.signature_main= signature_file_main_file
        if signature_buyer_id:
            signature_file_main_file = MainFile.objects.get(id=signature_buyer_id)
            signature_file_main_file.its_blong=True
            signature_file_main_file.save()
            new_invoice.signature_buyer= signature_file_main_file


        new_invoice.save()
        if payment_type == "installment":
            factor_price =new_invoice.factor_price()
            final_price = factor_price['final_price']
            installment_count = int(final_price) // int(installment_price)

            remaining = int(final_price) % int(installment_price)
            last_installment_date = new_invoice.created_date + timedelta(days=installment_period_day)
            for item in range(1,installment_count+1):
                new_installment = Installment.objects.create(
                    price = installment_price,
                    date_to_pay = last_installment_date,
                    invoice =new_invoice
                )
                last_installment_date = last_installment_date + timedelta(days=installment_period_day)
            if remaining > 0 :
                new_installment = Installment.objects.create(
                    price=installment_price,
                    date_to_pay=last_installment_date,
                    invoice =new_invoice
                )

        for product in products:
            new_product = ProductInvoice(**product)
            new_product.save()
            new_invoice.product.add(new_product)


        return new_invoice