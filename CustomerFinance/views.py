from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from CrmCore.models import *

from core.permission import IsAccess
from dotenv import load_dotenv
import os
load_dotenv()
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
# Invoice Manager Begin 


class InvoiceManager(APIView):
    permission_classes = [IsAuthenticated, IsAccess]
    
    def add_file_urls(self, invoice_obj):
        """Helper method to add signature and logo file URLs to the serialized invoice."""
        base_url = os.getenv("BASE_URL")
        try:
            data = {
                "signature_file": f"{base_url}{invoice_obj.signature_main.file.url}" if invoice_obj.signature_main else "",
                "logo_file": f"{base_url}{invoice_obj.logo_main.file.url}" if invoice_obj.logo_main else ""
            }
            return data
        except:
            return {
                "signature_file":"",
                "logo_file":"s"

            }
    
    def get(self, request, invoice_id=None):
        base_url = os.getenv("BASE_URL")
        
        if invoice_id:
            # Retrieve and serialize single invoice by ID
            invoice_obj = get_object_or_404(Invoice, id=invoice_id)
            invoice_data = InvoiceSerializer(invoice_obj).data
   

            invoice_data.update(self.add_file_urls(invoice_obj))
            return Response(
                status=status.HTTP_200_OK, 
                data={"message": "success", "status": True, "data": invoice_data}
            )
        
        # Retrieve all invoices for a specific customer
        customer_id = request.GET.get("customer_id")
        customer_obj = get_object_or_404(CustomerUser, id=customer_id)
        invoice_objs = customer_obj.invoice.all().order_by("-id")
        invoice_data_list = InvoiceSerializer(invoice_objs, many=True).data

        # Add file URLs to each serialized invoice
        for invoice_data in invoice_data_list:
            invoice_obj = Invoice.objects.get(id=invoice_data['id'])
            invoice_data.update(self.add_file_urls(invoice_obj))

        
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "success", "status": True, "data": invoice_data_list}
        )


    def post(self,request):
        data =request.data
        customer_id = data['customer_id']
        serializer_data = InvoiceSerializer(data= request.data)

        if serializer_data.is_valid():
            invoice_obj = serializer_data.create(validated_data=request.data)
            qr = qrcode.make("https://google.com")
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            random_number = random.randint(1,2312313)
            # Save QR code image
            invoice_obj.qr_code.file.save(f"{random_number}_1s.png", ContentFile(buffer.getvalue()), save=True)
            invoice_obj.save()
            response_data = InvoiceSerializer(invoice_obj).data
            
            customer_obj = CustomerUser.objects.get(id=customer_id)
            new_acction = ActionData(
                action_type="invoice",
                object_id = invoice_obj.id,
                user_author=request.user.id,

            )
            new_acction.save()
            new_report = Report(
                report_type =True,
                action_data =new_acction,
            )
            new_report.save()
            customer_obj.report.add(new_report)
            
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"succses",
                "data":response_data
            })

        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer_data.errors)
            



