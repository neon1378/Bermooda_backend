from django.shortcuts import render,redirect
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
import requests
import time
from datetime import datetime
from rest_framework import status
from .models import *
import random
from core.models import MainFile
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_payment (request):

    wallet_id = request.data.get("wallet_id")
    amount= request.data.get("amount",None)
    discount_id =request.data.get("discount_id",None)

    payment_method = request.data.get("payment_methods",None)
    plan_method = request.data.get("Plan_method",None)

    if payment_method and payment_method == "plan":
        if plan_method == "startup":
            amount= 65000000
        elif plan_method == "launching":
            amount = 130000000
        elif plan_method == "growth":
            amount = 280000000
        elif plan_method == "professional":
            amount = 450000000
        elif plan_method == "magician":
            amount =800000000
        elif plan_method == "ruby":
            amount =1300000000
        elif plan_method == "diamond":
            amount = 2600000000
        elif plan_method == "star":
            amount = 5000000000
    main_amount = amount
    if discount_id:
        discount_obj =Discount.objects.get(id=discount_id)
        amount = amount - (amount * discount_obj.percentage // 100)

    wallet_obj = get_object_or_404(Wallet,id=wallet_id)
    try:
        url = "https://gateway.zibal.ir/v1/request"
        call_back_url = "https://api.bermooda.app/v1/WalletManager/end_payment"
        payload = {
            "merchant":"677e70346f380300152c1acc",
            "amount":amount,
            "callbackUrl":call_back_url
            
            
        }
        
        
        response = requests.post(url=url,json=payload)
        response_data = response.json()

        price = int(amount)/10

        new_trans_action = WalletTransAction(
            track_id=response_data['trackId'],
            wallet=wallet_obj,
            price=int(main_amount)/10,
            trans_action_status = "deposit",
            order_id = f"D_{random.randint(9999,100000)}"

        )
        if payment_method and payment_method=="plan":
            new_trans_action.payment_method="PLAN"
            new_trans_action.plan_method =plan_method
        else:
            new_trans_action.payment_method="wallet"
        if discount_id:
            new_trans_action.discount_id=discount_id

        new_trans_action.save()
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"try again",
            "data":{}
        })
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":{
            "redirect_url":f"https://api.bermooda.app/v1/WalletManager/waiting_payment_page/{new_trans_action.track_id}"
        }
    })
    # return render(request,"WalletManager/start_payment.html",context={"trackId":response_data['trackId']})
    # return render(request,"WalletManager/start_payment.html")



def end_payment (request):
  
    track_id = request.GET.get("trackId")
    success= request.GET.get("success",None)
    trans_action_obj = WalletTransAction.objects.get(track_id=track_id)
    if not all([track_id, success ]):
        return JsonResponse({'error': 'Invalid data'}, status=400)
    try:
        if int(success) == 1 :
            with transaction.atomic():

                
                if trans_action_obj.status_deposit == False:
                    url ="https://gateway.zibal.ir/v1/verify"
                    payload= {
                        "merchant":"669387bc88b941001d98cbe6",
                        "trackId":trans_action_obj.track_id
                    }
                    response = requests.post(url=url,json=payload)
                    response_data = response.json()
                    if response_data['status'] == 1:
                        trans_action_obj.status_deposit = True
                        trans_action_obj.card_number = response_data['cardNumber']
                        trans_action_obj.paid_at = response_data['paidAt']
                        trans_action_obj.ref_number= response_data['refNumber']

                        trans_action_obj.wallet.balance  += trans_action_obj.price
                        trans_action_obj.wallet.save()
                        if trans_action_obj.wallet.balance > 0:
                            trans_action_obj.wallet.workspace.is_active = True
                            trans_action_obj.wallet.workspace.save()
                        trans_action_obj.wallet.workspace.payment_method = trans_action_obj.payment_method
                        trans_action_obj.wallet.workspace.plan_method = trans_action_obj.plan_method
                        trans_action_obj.wallet.workspace.plan_started_date = datetime.now()
                        if trans_action_obj.discount:
                            trans_action_obj.discount.is_active=False
                            trans_action_obj.discount.save()

                        trans_action_obj.wallet.workspace.save()
                        trans_action_obj.save()
                        #redirect to success
                        
                        return redirect(f"https://api.bermooda.app/v1/WalletManager/success_payment/{trans_action_obj.id}")
                    else:
                        return redirect(f"https://api.bermooda.app/v1/WalletManager/unsuccess_payment/{trans_action_obj.id}")
                        #redirect to not success
                        pass

                else:
                    return redirect(f"https://api.bermooda.app/v1/WalletManager/unsuccess_payment/{trans_action_obj.id}")
                    #redirect to not success
                    pass
        else:
            # trans_action_obj.delete()
            return redirect(f"https://office.bermooda.app")
    
    except:
        return redirect(f"https://api.bermooda.app/v1/WalletManager/unsuccess_payment/{trans_action_obj.id}")
        #redirect to not success
        pass
    
# 
            
    return render(request,"WalletManager/end_payment.html")



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trans_action_wallet(request,trans_action_id=None):
    workspace_id = request.GET.get("workspace_id")
    workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
    if request.user == workspace_obj.owner:
        if trans_action_id:
            trans_action= get_object_or_404(WalletTransAction,id=trans_action_id)
            if trans_action.trans_action_status == "deposit":
                    response_data ={
                        "track_id":trans_action.track_id,
                        "id":trans_action.id,
                        "jtime":trans_action.jtime(),
                        "price":f"{trans_action.price:,.0f}",
                        "ref_number":trans_action.ref_number,
                        "order_id":trans_action.order_id,
                        "card_number":trans_action.card_number,
                        "trans_action_status":trans_action.trans_action_status,
                        
                    }
            

        
            else:
                    response_data = {
                        "id":trans_action.id,
                        "jtime":trans_action.jtime(),
                        "price":f"{trans_action.price:,.0f}",
                        "order_id":trans_action.order_id,
                        "trans_action_status":trans_action.trans_action_status,
                        "total_mb":f"{trans_action.total_gb} MB",
                        "total_user":trans_action.total_user
                    }
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":response_data


            })
            

        wallet_obj = Wallet.objects.get(workspace = workspace_obj)
        wallet_trans_actions = WalletTransAction.objects.filter(status_deposit=True,wallet=wallet_obj).order_by("-id")
        response_data =[]
        for trans_action in wallet_trans_actions:
            if trans_action.trans_action_status == "deposit":
                dic ={
                    "track_id":trans_action.track_id,
                    "id":trans_action.id,
                    "jtime":trans_action.jtime(),
                    "price":f"{trans_action.price:,.0f}",
                    "ref_number":trans_action.ref_number,
                    "order_id":trans_action.order_id,
                    "card_number":trans_action.card_number,
                    "trans_action_status":trans_action.trans_action_status,
                    
                }
                response_data.append(dic)

    
            else:
                dic = {
                    "id":trans_action.id,
                    "jtime":trans_action.jtime(),
                    "price":f"{trans_action.price:,.0f}",
                    "order_id":trans_action.order_id,
                    "trans_action_status":trans_action.trans_action_status,
                    "total_mb":f"{trans_action.total_gb} MB",
                    "total_user":trans_action.total_user
                }
                response_data.append(dic)
        print(response_data)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":response_data


        })

    else:
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":False,
            "message":"access denied"
        })

             
    

@api_view(['GET'])
@permission_classes([AllowAny])
def create_workspaces (request):
    for workspace in WorkSpace.objects.all():
        try:
            wallet = Wallet.objects.get(workspace=workspace)
        except:
            new_wallet = Wallet(
                workspace=workspace,
                balance=0,
            )
            new_wallet.save()
    return Response(status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_detail (request):
    workspace_id= request.GET.get('workspace_id',None)
    if workspace_id:
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
    else:
        workspace_obj = get_object_or_404(WorkSpace,id=request.user.current_workspace_id)
        
        
    wallet_obj = Wallet.objects.get(workspace=workspace_obj)
    user_count = workspace_obj.workspace_member.all().count()
    main_files = MainFile.objects.filter(its_blong=True,workspace_id=str(workspace_obj.id))
    mb_count =0
    for file in main_files:
                
        try:
            file_size_in_bytes = file.file.size
            mb_count += file_size_in_bytes / (1024 * 1024)
        except:
            pass

    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":{
            "id":wallet_obj.id,
            "balance":f"{wallet_obj.balance:,.0f}",
            "user_count":user_count,
            "mb_count":int(mb_count),
        }
    })




def waiting_payment_page(request,track_id=None):
    if track_id:
        time.sleep(2.5)
        return redirect(f"https://gateway.zibal.ir/start/{track_id}")

    return render(request,"WalletManager/waiting_page.html")



def unsuccess_payment(request,trans_action_id=None):
    trans_action = trans_action= get_object_or_404(WalletTransAction,id=trans_action_id)
    context = {
        "track_id":trans_action.track_id,
        "id":trans_action.id,
        "jtime":trans_action.format_jalali_datetime(),
        "price":f"{trans_action.price:,.0f}",
        "ref_number":trans_action.ref_number,
        "order_id":trans_action.order_id,
        "card_number":trans_action.card_number,
        "trans_action_status":trans_action.trans_action_status,
    }
    return render(request,"WalletManager/unsuccess_payment.html",context=context)

def success_payment(request,trans_action_id=None):
    trans_action = trans_action= get_object_or_404(WalletTransAction,id=trans_action_id)
    context = {
        "track_id":trans_action.track_id,
        "id":trans_action.id,
        "jtime":trans_action.format_jalali_datetime(),
        "price":f"{trans_action.price:,.0f}",
        "ref_number":trans_action.ref_number,
        "order_id":trans_action.order_id,
        "card_number":trans_action.card_number,
        "trans_action_status":trans_action.trans_action_status,
    }
    return render(request,"WalletManager/success_payment.html",context=context)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_discount_code(request):
    code = request.GET.get("code")
    if not code:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"کد تخفیف اجباری میباشد",

        })
    try:
        discount_obj =Discount.objects.get(code=code)
        if not discount_obj.is_active:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"کد تخفیف وارد شده قبلا استفاده شده است"
            })
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"تخفیف با موفقیت به صورت حساب شما اضافه شد",
            "data":{
                "id":discount_obj.id,
                "code":discount_obj.code,
                "percentage":discount_obj.percentage

            }
        })
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"کد تخفیف معتبر نمیباشد",

        })