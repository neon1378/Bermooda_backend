from multiprocessing.util import is_exiting

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
from core.views import  send_invite_link

class IndustrialActivitySerializer(ModelSerializer):
    class Meta:
        model =IndustrialActivity
        fields = [
            "id",
            "title"
        ]

class WorkSpaceSerializer(ModelSerializer):
    industrialactivity_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model =WorkSpace
        fields =[
            "id",
            "industrialactivity_id",

            "business_type",

            "reference_sub_category",
            "reference_category",
            "jadoo_brand_name",
            "business_detail",
            "city",
            "state",
            "state_name",
            "city_name",
            "main_category_data",
            "sub_category_data"
        ]
    def update(self,instance,validated_data):
        
        jadoo_brand_name= validated_data.get("jadoo_brand_name",None)
        if jadoo_brand_name == None:
            raise serializers.ValidationError({"error":{
                "detail":"نام پروفایل اجباری میباشد"
            }})
        if WorkSpace.objects.filter(jadoo_brand_name=jadoo_brand_name).exists():
            if instance.jadoo_brand_name != jadoo_brand_name:
                raise serializers.ValidationError({"error":{
                "detail":"نام پروفایل انتخاب شده درحال حاضر وجود دارد"
                }})
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
                return item




        new_workspace_member = WorkspaceMember.objects.create(**validated_data)
        new_workspace_member.user_account = user_acc
        new_workspace_member.save()
        send_invite_link(user_acc.phone_number, new_workspace_member.workspace.owner.fullname,
                            new_workspace_member.workspace.title)


        return new_workspace_member