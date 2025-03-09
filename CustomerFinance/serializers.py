from celery.bin.worker import worker
from django.utils.text import normalize_newlines
from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers
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



class InvoiceSerializer(ModelSerializer):
    seller_information = InformationSerializer(read_only=True)
    buyer_information = InformationSerializer(read_only=True)
    product= ProductInvoiceSerializer(many=True,read_only=True)
    workspace_id= serializers.IntegerField(read_only=True)
    signature_id =serializers.IntegerField(write_only=True,required=False)
    product_list= serializers.ListField(write_only=True,required=True)
    status = InvoiceStatusSerializer(read_only=True)
    status_id = serializers.IntegerField(write_only=True,required=False)
    seller_information_data =serializers.JSONField(write_only=True,required=True)

    class Meta:
        model = Invoice
        fields = [
            "status",
            "status_id",
            "id",
            "signature_url",
            "logo_url",
            "payment_type",
            "seller_information",
            "buyer_information",
            "product",
            "created_date",
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

            "seller_information_data",
      
        ]



    def create(self,validated_data):
        workspace_id =validated_data.pop("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        products = validated_data.pop("product_list",[])
        signature_id = validated_data.pop("signature_id",None)


        seller_information = validated_data.pop("seller_information_data")



   
        customer_id= validated_data.pop("customer_id")

        if not workspace_obj.personal_information_status:
            raise serializers.ValidationError({
                "status":False,
                "message":"not_information",
                "data":{},
            })

        buyer_information_obj = Information(
            fullname_or_company_name =workspace_obj.jadoo_brand_name,
            email = workspace_obj.email,
            address = workspace_obj.address,
            city = workspace_obj.city,
            state = workspace_obj.state,
            phone_number = workspace_obj.phone_number,
        )
        buyer_information_obj.save()
        seller_information_obj = Information(
            
            **seller_information,

            
        )
        if seller_information['state']:
            state= State.objects.get(id=seller_information['state'])
            seller_information_obj.state =state
        if seller_information['city']:
            city= City.objects.get(id=seller_information['city'])
            seller_information_obj.city =city

        seller_information_obj.save()
        new_invoice = Invoice(
            **validated_data,
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
            new_invoice.signature_main_id= signature_file_main_file

        new_invoice.save()
        for product in products:
            new_product = ProductInvoice(**product)
            new_product.save()
            new_invoice.product.add(new_product)

        customer_obj = get_object_or_404(CustomerUser,id=customer_id)
        customer_obj.invoice.add(new_invoice)
        return new_invoice