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
            "formated_price",
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
    document_of_payment = MainFileSerializer(read_only=True,many=True)
    document_of_payment_id_list =serializers.ListField(write_only=True,required=False)

    class Meta:
        model = Installment
        fields =[
            "id",
            "order",
            "price",
            "date_to_pay",
            "invoice",
            "is_paid",
            "date_payed",
            "is_delayed",
            "document_of_payment",
            "document_of_payment_id_list",
            "days_passed",
            "created_persian",
            "date_to_pay_persian",
            "date_payed_persian",
        ]











class InvoiceSerializer(ModelSerializer):
    qr_code = MainFileSerializer(read_only=True)

    installments = InstallMentSerializer(read_only=True,many=True)
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
    date_to_pay_jalali = serializers.CharField(write_only=True,required=False,allow_null=True)
    validity_date = serializers.CharField(write_only=True,required=False)
    class Meta:
        model = Invoice
        fields = [
            "status",
            "date_to_pay_jalali",
            "invoice_type",
            "status_id",
            "qr_code",
            "id",
            "main_id",
            "signature_url",
            "is_paid",
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


            "installments",
            "seller_information_data",

            "interest_percentage",

            "created_date_persian",
            "validity_date_persian",
            "is_over",
            "date_to_pay_persian",
            "date_payed_persian",
      
        ]



    def create(self,validated_data):


        workspace_id =validated_data.pop("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        products = validated_data.pop("product_list",[])
        signature_id = validated_data.pop("signature_id",None)

        installment_payments = validated_data.pop("installment_payments",None)

        created_date = validated_data.pop("created_date",None)
        validity_date = validated_data.pop("validity_date",None)
        signature_buyer_id= validated_data.pop("signature_buyer_id",None)
        seller_information = validated_data.pop("seller_information_data")

        state_seller = seller_information.pop("state",None)
        city_seller = seller_information.pop("city",None)
        payment_type = validated_data.get("payment_type",None)

        date_to_pay_jalali = validity_date.pop("date_to_pay_persian",None)
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
        if date_to_pay_jalali:
            new_invoice.date_to_pay=persian_to_gregorian(date_to_pay_jalali)


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

        for product in products:
            new_product = ProductInvoice(**product)
            new_product.save()
            new_invoice.product.add(new_product)
        if payment_type == "installment":
            # try:
            for installment in installment_payments:
                new_installment = Installment.objects.create(price=installment['price'],date_to_pay=persian_to_gregorian(installment['date_to_pay']),invoice=new_invoice)
            # except:
            #     raise serializers.ValidationError(
            #         {
            #             "status":False,
            #             "message":"Validation Error",
            #             "data":{}
            #         }
            #     )




        return new_invoice





class PayTheInvoiceSerializer(serializers.ModelSerializer):
    payment_documents = MainFileSerializer(many=True,read_only=True)
    payment_document_id_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    date_payed_jalali = serializers.CharField(write_only=True,required=True)
    class Meta:
        model = Invoice
        fields =[
            "id",
            "date_payed_jalali",
            "is_paid",
            "payment_documents",
            "date_to_pay_persian",
            "date_payed_persian",
        ]
    def update(self, instance, validated_data):
        instance.date_payed = persian_to_gregorian(validated_data.get("date_payed_jalali"))
        payment_document_id_list  = validated_data.pop("payment_document_id_list",None)
        if payment_document_id_list:
            for file_id in payment_document_id_list:
                main_file= MainFile.objects.get(id=file_id)
                main_file.its_blong=True
                main_file.save()
                instance.payment_documents.add(main_file)
        instance.is_paid=True
        instance.save()