import os
from multiprocessing.util import is_exiting

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
import requests
from django.shortcuts import get_object_or_404
from core.views import  send_invite_link
from WorkSpaceChat.serializers import  GroupSerializer
class IndustrialActivitySerializer(ModelSerializer):
    class Meta:
        model =IndustrialActivity
        fields = [
            "id",
            "title"
        ]


class UpdateWorkSpaceSerializer(ModelSerializer):
    user_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = WorkSpace
        fields =[
            "user_id",
            "id",
            "title",
            "business_detail",
            "personal_information_status",
            "person_type",
            # personal and  legal fields
            "national_code",
            "email",
            "postal_code",
            "bank_number",
            "phone_number",
            # Legal Fields
            "tel_number",
            "fax_number",
            "economic_number",
            "address",

        ]

    def update(self, instance, validated_data):
        user_id = validated_data.pop("user_id")
        user = UserAccount.objects.get(id=user_id)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        jadoo_base_url = os.getenv("JADOO_BASE_URL")
        url = f"{jadoo_base_url}/workspace/update/{instance.jadoo_workspace_id}"
        headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {request.user.refrence_token}"
        }
        payload = {
            "name":instance.title ,
            "bio":instance.business_detail ,
            "username":instance.business_detail,
        }

        try:
            requests.put(url=url,data=payload,headers=headers)
        except:
            pass
        return instance



class WorkSpaceSerializer(ModelSerializer):
    industrialactivity_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model =WorkSpace
        fields =[
            "id",
            "industrialactivity_id",
            "personal_information_status",
            "business_type",


            "jadoo_brand_name",
            "business_detail",
            "city",
            "state",
            "state_name",
            "city_name",
            "main_category_data",
            "business_employer",
            "sub_category_data",
            # personal and  legal fields
            "person_type",
            "national_code",
            "email",
            "postal_code",
            "bank_number",
            "phone_number",
            # Legal Fields
            "tel_number",
            "fax_number",
            "economic_number",
            "address",
        ]
    def update(self,instance,validated_data):
        
        jadoo_brand_name= validated_data.get("jadoo_brand_name",None)
        if not jadoo_brand_name :
            raise serializers.ValidationError({
                "status":False,
                "message":"نام کاربری اجباری میباشد"
            })
        if WorkSpace.all_objects.filter(jadoo_brand_name=jadoo_brand_name).exists() :
            if instance.jadoo_brand_name != jadoo_brand_name:
                raise serializers.ValidationError({
                    "status":False,
                    "message":"نام کاربری وارد شده در حال حاضر وجود دارد"
                })
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
class UserSerializer(serializers.ModelSerializer):
    avatar_id = serializers.IntegerField(write_only=True,required=False)

    class Meta:
        model = UserAccount
        fields = [

            "id",
            "avatar_id",
            "phone_number",
            "avatar_url_main",
            "is_register",




        ]

class WorkSpaceMemberSerializer(serializers.ModelSerializer):
    user_account_data =serializers.JSONField(write_only=True,required=True)
    user_account = UserSerializer(required=False,read_only=True)
    workspace_id= serializers.IntegerField(required=True,write_only=True)
    permissions = serializers.ListField(write_only=True,required=True)

    class Meta:
        model = WorkspaceMember
        fields = [
        "id",
        "user_account_data",
        "user_account",
        "first_name",
        "is_accepted",
        "permissions",
        "last_name",
        "workspace_id",
        "jtime",
        "permission_list",
        ]

    def create(self, validated_data):
        workspace_id = validated_data.get("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        user_account = validated_data.pop("user_account_data")

        permissions= validated_data.pop("permissions")
        try :

            user_acc = UserAccount.objects.get(phone_number=user_account.get("phone_number"))


        except:
            user_acc = UserAccount(phone_number=user_account.get("phone_number"))
            user_acc.is_register=False
            user_acc.save()
        if WorkspaceMember.objects.filter(workspace=workspace_obj,user_account=user_acc).exists() or workspace_obj.owner == user_acc:
            raise serializers.ValidationError({
                "status": False,
                "message": "کاربر مورد نظر در حال حاظر در تیم شما وجود دارد",
                "data": {}
            })
        # try:
        member_obj_deleted = WorkspaceMember.all_objects.filter(is_deleted=True)

        for item in member_obj_deleted:
            if item.workspace == workspace_obj and item.user_account == user_acc:

                item.is_deleted = False
                item.deleted_at =None
                first_name = validated_data.get("first_name")
                last_name =validated_data.get("last_name")
                item.first_name = first_name
                item.last_name = last_name
                item.fullname = f"{first_name} {last_name}"
                if item.user_account.current_workspace_id == 0 or not WorkSpace.objects.filter(id=item.user_account.current_workspace_id).exists():
                    item.user_account.current_workspace_id=workspace_obj.id
                    item.user_account.save()
                item.save()
                return item




        new_workspace_member = WorkspaceMember.objects.create(**validated_data)
        new_workspace_member.fullname = f"{new_workspace_member.first_name} {new_workspace_member.last_name}"
        new_workspace_member.user_account = user_acc
        new_workspace_member.is_accepted= False
        new_workspace_member.save()

        send_invite_link(user_acc.phone_number, new_workspace_member.workspace.owner.fullname,
                            new_workspace_member.workspace.title)
        from .views import  create_permission_for_member
        create_permission_for_member(member_id=new_workspace_member.id, permissions=permissions)

        new_workspace_member.user_account.current_workspace_id=workspace_obj.id
        new_workspace_member.user_account.save()
        # create group messages
        group_message = GroupSerializer(data={
            "workspace_id":workspace_obj.id,
            "member_id_list":[workspace_obj.owner.id,new_workspace_member.user_account.id]

        })
        if group_message.is_valid():
            group_message.save()
        for member in WorkspaceMember.objects.filter(workspace=workspace_obj):
            if member.id !=new_workspace_member:

                group_message_member =GroupSerializer(
                    data={
                        "workspace_id": workspace_obj.id,
                        "member_id_list": [member.user_account.id, new_workspace_member.user_account.id]

                    }
                )
                if group_message_member.is_valid():
                    group_message_member.save()


        return new_workspace_member