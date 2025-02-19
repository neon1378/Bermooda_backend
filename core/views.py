from django.shortcuts import render
from dotenv import load_dotenv
import os
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from .models import MainFile
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import requests
from rest_framework.permissions import IsAuthenticated,AllowAny
load_dotenv()
import re

# Create your views here.
def send_sms (phone_number,verify_code ):
    api_key = "6865587A4B6D694F2F39556156724B53674F386142593074583545495859734C52414A4B46384C336543383D"
    
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json?receptor={phone_number}&token={verify_code}&template=verifycode"
    response = requests.get(url=url)


def send_invite_link (phone_number,workspace_owner,workspace_name):
    try:
    # main_workspace_name =workspace_name.replace(" ", "\u200C")
    # main_workspace_owner = workspace_owner.replace(" ", "\u200C")
    # print(main_workspace_owner,"@")
    # print(main_workspace_name,"!")
        main_workspace_name = workspace_name.replace(" ","\u205f")
        main_workspace_owner = workspace_owner.replace(" ","\u205f")


        api_key =os.getenv('KAVE_NEGAR_API_KEY')
        print(api_key,"@@@@")
        url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json?token={main_workspace_owner}&token2={main_workspace_name}&receptor={phone_number}&template=invitelink"

        response = requests.get(url=url)
        print(response.json())

    except:
        pass

def send_sms_core(fullname,phone_number):
        try:
            main_fullname = fullname.replace(" ", "\u205f")
            api_key =  os.getenv('KAVE_NEGAR_API_KEY')
            url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json?token={main_fullname}&receptor={phone_number}&template=walletwarrning"
            response = requests.get(url=url)
            print(response.json())
        except:
            pass

@parser_classes([MultiPartParser, FormParser])
@api_view(['POST']) 
@permission_classes([AllowAny])
def upload_file (request):
    
    file = request.FILES.get("file")
    new_file = MainFile(file=file)
    try:
        new_file.workspace_id =request.data['workspace_id']
    except:
        pass
    new_file.save()
    
    return Response(status=status.HTTP_201_CREATED,data={
        "status":True,
        "message":"succses",
        "data":{
            "file_id":new_file.id,
            "url":new_file.file.url,
            "file_name":new_file.file.name,
        }
    })



