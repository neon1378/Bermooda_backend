from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import *
from rest_framework.decorators import  api_view,permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from CrmCore.models import *
from core.widgets import get_client_ip
from core.views import send_sms
from datetime import datetime
from core.permission import IsAccess
from dotenv import load_dotenv
import os
load_dotenv()
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
# Invoice Manager Begin 


class InvoiceManager(APIView):
    permission_classes = [IsAuthenticated]
    
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
        invoice_objs =Invoice.objects.filter(customer=customer_obj).order_by("-id")
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
        request.data['workspace_id'] = request.user.current_workspace_id
        serializer_data = InvoiceSerializer(data= request.data)

        if serializer_data.is_valid():
            invoice_obj = serializer_data.create(validated_data=request.data)
            front_base_url = os.getenv("FRONT_BASE_URL")
            qr = qrcode.make(f"{front_base_url}/factor/{invoice_obj.main_id}")
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            random_number = random.randint(1,2312313)
            # Save QR code image
            new_main_file = MainFile()
            new_main_file.save()
            new_main_file.file.save(f"{random_number}_1s.png", ContentFile(buffer.getvalue()), save=True)
            new_main_file.its_blong=True
            new_main_file.workspace_id=request.user.current_workspace_id
            new_main_file.save()
            invoice_obj.qr_code=new_main_file
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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_invoice_status(request,invoice_id):
    data= request.data
    invoice_obj = get_object_or_404(Invoice,id=invoice_id)
    status_id = data['status_id']
    status_obj = get_object_or_404(InvoiceStatus,id=status_id)
    invoice_obj.status= status_obj
    invoice_obj.save()
    serializer_data =InvoiceSerializer(invoice_obj)
    return Response(
        status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"با موفقیت انجام شد ",
            "data":serializer_data.data
        }
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def invoice_preview(request,invoice_id):
    invoice_obj = get_object_or_404(Invoice,main_id=invoice_id)
    ip_address = get_client_ip(request)
    # if ip_address != invoice_obj.login_ip or not invoice_obj.is_expired():
    #     return Response(status=status.HTTP_403_FORBIDDEN,data={
    #         "status":False,
    #         "message":"Access Denied",
    #         "data":{}
    #     })

    serializer_data =InvoiceSerializer(invoice_obj)
    return Response(
        status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data
        },

    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request,invoice_id):
    data =request.data
    invoice_obj = get_object_or_404(Invoice,main_id=invoice_id)
    phone_number  = data.get("phone_number")
    if invoice_obj.customer.phone_number != phone_number:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"شماره تلفن وارد شده اشتباه میباشد"
        })


    random_number= random.randint(100000, 999999)
    invoice_obj.verify_code =random_number

    invoice_obj.save()
    send_sms(phone_number=invoice_obj.customer.phone_number,verify_code=invoice_obj.verify_code)
    return Response(status=status.HTTP_202_ACCEPTED,data={
        "status":True,
        "message":"کد تایید با موفقیت ارسال شد",
        "data":{
            "phone_number":phone_number
        }
    })




@api_view(['POST'])
@permission_classes([AllowAny])
def verification_code(request,invoice_id):
    data = request.data
    invoice_obj = get_object_or_404(Invoice, main_id=invoice_id)
    code = data.get("code")
    if int(invoice_obj.verify_code) != int(code):
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"کد تایید وارد شده اشتباه میباشد",
            "data":{}
        })
    ip_address = get_client_ip(request)
    invoice_obj.login_ip = ip_address
    invoice_obj.date_time_to_login=datetime.now()
    invoice_obj.save()
    return Response(status=status.HTTP_202_ACCEPTED,data={
        "status":True,
        "message":"با موفقیت انجام شد",
        "data":{}
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_buyer_signature(request,invoice_id):
    invoice_obj = get_object_or_404(Invoice,main_id=invoice_id)
    ip_address = get_client_ip(request)
    if ip_address != invoice_obj.login_ip or not invoice_obj.is_expired():
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"Access Denied",
            "data":{}
        })
    data =request.data
    try:
        signature_id = data.get("signature_id")
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"signature_id its required"
        })
    main_file = MainFile.objects.filter(id=signature_id).first()
    if main_file:
        main_file.its_blong =True
        main_file.save()

        invoice_obj.signature_buyer = main_file
        invoice_obj.save()
        return Response(status=status.HTTP_201_CREATED,data={
            "status":True,
            "message":"با موفقیت ثبت شد ",
            "data":MainFileSerializer(main_file).data
        })
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invoice_code (request):

    while True:
        random_number = random.randint(1, 100000)
        if not Invoice.objects.filter(invoice_code=f"#{random_number}").exists():
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":{
                    "invoice_code":f"#{random_number}"
                }
            })







class InstallMentView(APIView):
    def get(self,request,installment_id=None):
        if installment_id:
            installment_obj = get_object_or_404(Installment,id=installment_id)
            serializer_data = InstallMentSerializer(installment_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        invoice_id = request.GET.get("invoice_id")
        invoice_obj = get_object_or_404(Invoice,id=invoice_id)
        installment_objs = Installment.objects.filter(invoice=invoice_obj).order_by("-date_to_pay")
        order= 1
        for obj in installment_objs:
            obj.order=order
            obj.save()
            order+=1

        serializer_data = InstallMentSerializer(installment_objs,many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت انجام شد",
            "data":serializer_data.data
        })


    def post(self,request):
        data= request.data
        installment_list= data.get("installment_list")
        installment_objs = []
        for installment in installment_list:
            installment_id = installment.get("installment_id")
            installment_obj = get_object_or_404(Installment,id=installment_id)
            installment_objs.append(installment_obj)
            document_of_payment_id_list = installment.get("document_of_payment_id_list",[])
            # is_paid = installment.get("is_paid")
            date_payed_jalali = installment.get("date_payed_jalali")
            for  document_of_payment_id in document_of_payment_id_list:
                main_file = MainFile.objects.get(id=document_of_payment_id)
                main_file.its_blong = True
                main_file.save()
                installment_obj.document_of_payment.add(main_file)

            installment_obj.date_payed = persian_to_gregorian(date_payed_jalali)
            installment_obj.is_paid = True
            installment_obj.save()
        serializer_data= InstallMentSerializer(installment_objs,many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت ثبت شد",
            "data":serializer_data.data
        })





class PayTheInvoiceView(APIView):
    def get(self,request,invoice_id=None):
        if not invoice_id:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"شناسه فاکتور الزامی میباشد",

            })
        invoice_obj = get_object_or_404(Invoice,id=invoice_id)
        serializer_data =PayTheInvoiceSerializer(invoice_obj)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":serializer_data.data
        })
    def put(self,request,invoice_id):
        invoice_obj= get_object_or_404(Invoice,id=invoice_id)
        serializer_data = PayTheInvoiceSerializer(instance=invoice_obj,data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت انجام شد",
                "data":serializer_data.data
            })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "Validation Error",
            "data": serializer_data.errors
        })
