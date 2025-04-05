import os
from multiprocessing.util import is_exiting
from core.serializers import MainFileSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from core.widgets import change_current_workspace_jadoo
from .models import *
import requests
from django.shortcuts import get_object_or_404
from core.views import  send_invite_link
from WorkSpaceChat.serializers import  GroupSerializer
from WorkSpaceChat.models import  GroupMessage
class IndustrialActivitySerializer(ModelSerializer):
    class Meta:
        model =IndustrialActivity
        fields = [
            "id",
            "title"
        ]


class UpdateWorkSpaceSerializer(ModelSerializer):
    user_id = serializers.IntegerField(write_only=True,required=False)
    national_card_image =MainFileSerializer(read_only=True)
    national_card_image_id = serializers.IntegerField(write_only=True,required=False)
    document_image =MainFileSerializer(read_only=True)
    document_image_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = WorkSpace
        fields =[
            "national_card_image",
            "national_card_image_id",
            "document_image",
            "document_image_id",
            "user_id",
            "company_name",
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
        national_card_image_id = validated_data.pop("national_card_image_id",None)
        document_image_id = validated_data.pop("document_image_id",None)
        user_id = validated_data.pop("user_id")
        user = UserAccount.objects.get(id=user_id)
        permission_list= validated_data.pop("permission_list",[])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        jadoo_base_url = os.getenv("JADOO_BASE_URL")
        url = f"{jadoo_base_url}/workspace/update/{instance.jadoo_workspace_id}"
        headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {user.refrence_token}"
        }
        payload = {
            "name":instance.title ,
            "bio":instance.business_detail ,
            "username":instance.business_detail,
        }
        if national_card_image_id:
            main_file = MainFile.objects.filter(id=national_card_image_id).first()
            if main_file:
                main_file.its_blong = True
                main_file.save()
                instance.national_card_image = main_file
        if document_image_id:
            main_file = MainFile.objects.filter(id=document_image_id).first()
            if main_file:
                main_file.its_blong = True
                main_file.save()
                instance.document_image = main_file
        instance.save()
        try:
            requests.put(url=url,data=payload,headers=headers)
        except:
            pass


        return instance

class WorkSpacePermissionSerializer(ModelSerializer):
    class Meta:
        model = WorkSpacePermission
        fields =[
            "id",
            "permission_type",
            "is_active"
        ]


class IndustrialActivitySerializer(ModelSerializer):
    class Meta:
        model= IndustrialActivity
        fields = [
            "id",
            "title"
        ]


class WorkSpaceSerializer(ModelSerializer):
    industrialactivity_id = serializers.IntegerField(write_only=True,required=True)
    permissions = WorkSpacePermissionSerializer(read_only=True,many=True)
    national_card_image_id = serializers.IntegerField(write_only=True,required=False)
    document_image_id = serializers.IntegerField(write_only=True,required=False)
    industrialactivity = IndustrialActivitySerializer(read_only=True)
    document_image = MainFileSerializer(read_only=True)
    national_card_image = MainFileSerializer(read_only=True)

    class Meta:
        model =WorkSpace
        fields =[
            "id",
            "industrialactivity_id",
            "industrialactivity",
            "personal_information_status",
            "business_type",
            "document_image",
            "national_card_image",
            "permissions",
            "company_name",
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
            "national_card_image_id",
            "document_image_id",
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

        national_card_image_id = validated_data.pop("national_card_image_id",None)
        document_image_id = validated_data.pop("document_image_id",None)
        jadoo_brand_name= validated_data.get("jadoo_brand_name",None)
        if not jadoo_brand_name :
            raise serializers.ValidationError({
                "status":False,
                "message":"نام کاربری اجباری میباشد"
            })
        if WorkSpace.objects.filter(jadoo_brand_name=jadoo_brand_name).exists() :
            if instance.jadoo_brand_name != jadoo_brand_name:
                raise serializers.ValidationError({
                    "status":False,
                    "message":"نام کاربری وارد شده در حال حاضر وجود دارد"
                })
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if national_card_image_id:
            main_file = MainFile.objects.filter(id=national_card_image_id).first()
            if main_file:
                main_file.its_blong = True
                main_file.save()
                instance.national_card_image = main_file
        if document_image_id:
            main_file = MainFile.objects.filter(id=document_image_id).first()
            if main_file:
                main_file.its_blong = True
                main_file.save()
                instance.document_image = main_file
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
        "is_team_bonos_status",
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
        if not GroupMessage.objects.filter(
            workspace = workspace_obj,
            members=workspace_obj.owner
        ).filter(members=new_workspace_member.user_account).exists():
            group_message = GroupMessage.objects.create(workspace=workspace_obj)
            group_message.members.set([workspace_obj.owner, new_workspace_member.user_account])


        workspace_members = WorkspaceMember.objects.filter(workspace=workspace_obj)
        for member in workspace_members:
            if member != new_workspace_member:
                if not GroupMessage.objects.filter(
                    workspace = workspace_obj,
                    members = new_workspace_member.user_account
                ).filter(members=member.user_account).exists():
                    group_message = GroupMessage.objects.create(workspace=workspace_obj)
                    group_message.members.set([member.user_account, new_workspace_member.user_account])

        send_invite_link(user_acc.phone_number, new_workspace_member.workspace.owner.fullname,
                            new_workspace_member.workspace.title)
        from .views import  create_permission_for_member
        create_permission_for_member(member_id=new_workspace_member.id, permissions=permissions)

        new_workspace_member.user_account.current_workspace_id=workspace_obj.id
        change_current_workspace_jadoo(user_acc=new_workspace_member.user_account,workspace_obj=workspace_obj)
        new_workspace_member.user_account.save()
        # create group messages

        try:
            base_url = os.getenv("JADOO_BASE_URL")
            url = f"{base_url}/workspace/addWorkSpaceMember"

            headers = {
                "content-type": "application/json",
                "Authorization": f"Bearer {new_workspace_member.workspace.owner.refrence_token}"
            }
            payload = {
                "workSpaceId": new_workspace_member.workspace.jadoo_workspace_id,
                "userId": new_workspace_member.user_account.refrence_id,
                "businessUserId": new_workspace_member.user_account.id,
                "businessMemberId": new_workspace_member.id,
            }
            response = requests.post(url=url, headers=headers, json=payload)
            print(response.json())
        except:
            pass
        return new_workspace_member