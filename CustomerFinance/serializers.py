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
    

class ProductInvoiceSerializer(ModelSerializer):
    class Meta:
        model = ProductInvoice
        fields = "__all__"


class InvoiceSerializer(ModelSerializer):
    seller_information = InformationSerializer()
    buyer_information = InformationSerializer()
    product= ProductInvoiceSerializer(many=True)
    class Meta:
        model = Invoice
        fields = [
            "id",
            "title",
            "seller_information",
            "buyer_information",
            "product",
            "description",
            "discount",
            "taxes",
            "created",
            "invoice_code",
            "factor_price",
            "invoice_date",
      
        ]



    def create(self,validated_data):
        workspace_id =validated_data.pop("workspace_id")
        products = validated_data.pop("product")
        signature_file = validated_data.pop("signature_file",None)
        logo_file = validated_data.pop("logo_file",None)
        buyer_information = validated_data.pop("buyer_information")
        seller_information = validated_data.pop("seller_information")
        buyer_city = buyer_information.pop("city_buyer")
        buyer_state = buyer_information.pop("state_buyer")


        sller_state = seller_information.pop("state_seller")
        sller_city = seller_information.pop("city_seller")
   
        customer_id= validated_data.pop("customer_id")
        buyer_information_obj = Information(
            **buyer_information,
            city_id =buyer_city,
            state_id = buyer_state
        )
        buyer_information_obj.save()
        seller_information_obj = Information(
            
            **seller_information,
            city_id =sller_state,
            state_id =sller_city
            
        )
        seller_information_obj.save()
        new_invoice = Invoice(
            **validated_data,
            buyer_information=buyer_information_obj,
            seller_information=seller_information_obj,
            invoice_code = f"#{random.randint(1,100000)}",
            signature_main_id = signature_file,
            logo_main_id = logo_file,          
        )
        try:
            signature_file_main_file = MainFile.objects.get(id=signature_file)
            logo_file_main_file = MainFile.objects.get(id=logo_file)
            signature_file_main_file.its_blong=True
            logo_file_main_file.its_blong=True
            signature_file_main_file.save()
            logo_file_main_file.save()
        except:
            pass
        new_invoice.save()
        for product in products:
            new_product = ProductInvoice(**product)
            new_product.save()
            new_invoice.product.add(new_product)

        customer_obj = get_object_or_404(CustomerUser,id=customer_id)
        customer_obj.invoice.add(new_invoice)
        return new_invoice