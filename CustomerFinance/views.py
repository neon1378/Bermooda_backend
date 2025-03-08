from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status,viewsets
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
                "logo_file":""

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


            
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"succses",
                "data":response_data
            })

        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer_data.errors)


class InvoiceStatusManager(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        group_crm_id = request.GET.get("group_crm_id")
        if not group_crm_id:
            return Response({
                "status": False,
                "message": "validation error",
                "data": {"group_crm_id": ["this field is required"]}
            }, status=status.HTTP_400_BAD_REQUEST)

        group_crm_obj = get_object_or_404(GroupCrm, id=group_crm_id)
        queryset = InvoiceStatus.objects.filter(group_crm=group_crm_obj)
        serializer = InvoiceStatusSerializer(queryset, many=True)
        return Response({
            "status": True,
            "message": "موفق",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = InvoiceStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "با موفقیت ثبت شد ",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": False,
            "message": "validation error",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class InvoiceStatusDetailManager(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, status_id):
        invoice_status_obj = get_object_or_404(InvoiceStatus, id=status_id)
        serializer = InvoiceStatusSerializer(invoice_status_obj)
        return Response({
            "status": True,
            "message": "موفق",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, status_id):
        invoice_status_obj = get_object_or_404(InvoiceStatus, id=status_id)
        serializer = InvoiceStatusSerializer(instance=invoice_status_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "با موفقیت بروزرسانی شد",
                "data": serializer.data
            }, status=status.HTTP_202_ACCEPTED)
        return Response({
            "status": False,
            "message": "validation error",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, status_id, *args, **kwargs):
        invoice_status_obj = get_object_or_404(InvoiceStatus, id=status_id)
        invoice_status_obj.delete()
        return Response({
            "status": True,
            "message": "با موفقیت حذف شد"
        }, status=status.HTTP_204_NO_CONTENT)