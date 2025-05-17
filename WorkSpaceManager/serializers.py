import os

from core.serializers import MainFileSerializer,StateSerializer,CitySerializer
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
import jdatetime

from core.widgets import change_current_workspace_jadoo,persian_to_gregorian,ExternalApi
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
    avatar = MainFileSerializer(read_only=True)
    class Meta:
        model =WorkSpace
        fields =[
            "title",
            "id",
            "industrialactivity_id",
            "auth_status",
            "industrialactivity",
            "personal_information_status",
            "business_type",
            "wallet_balance",
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
            "avatar",


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

class WorkSpaceMemberSerializer (serializers.ModelSerializer):
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
            try:
                jadoo_base_url = os.getenv("JADOO_BASE_URL")
                # send user to jadoo

                url = f"{jadoo_base_url}/user/auth/createBusinessUser"
                payload = {
                    "mobile": user_acc.phone_number,

                    "password": "asdlaskjd",

                }
                response_data = requests.post(url=url, data=payload)
                print(response_data.json())
                recive_data = response_data.json()

                user_acc.refrence_id = int(recive_data['data']['id'])
                user_acc.refrence_token = recive_data['data']['token']
                user_acc.save()
            except:
                pass
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

                item.is_accepted =False
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
            api_connection = ExternalApi(token=new_workspace_member.workspace.owner.refrence_token)

            response_data = api_connection.post(
                data={
                "workSpaceId": new_workspace_member.workspace.jadoo_workspace_id,
                "userId": new_workspace_member.user_account.refrence_id,
                "businessUserId": new_workspace_member.user_account.id,
                "businessMemberId": new_workspace_member.id,
                    },
                end_point="/workspace/addWorkSpaceMember"
            )
        except:
            pass







        return new_workspace_member


class StudyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model =StudyCategory
        fields = [
            "id",
            "title"
        ]

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields =[
            "id",
            "title"
        ]
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "id",
            "title"
        ]


class WorkSpaceMemberFullDataSerializer(serializers.ModelSerializer):
    folder_slug = serializers.IntegerField(required=False,allow_null=True)
    user_account = UserSerializer(required=False, read_only=True)
    workspace_id = serializers.IntegerField(required=True, write_only=True)
    permissions = serializers.ListField(write_only=True, required=False)
    state_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    city_id= serializers.IntegerField(write_only=True,required=False,allow_null=True)
    state = StateSerializer(read_only=True)
    city= CitySerializer(read_only=True)
    bad_record = MainFileSerializer(read_only=True)
    bad_record_id = serializers.IntegerField(write_only=True,required=False)
    date_of_birth_jalali = serializers.CharField(write_only=True,required=False,allow_null=True,allow_blank=True)
    date_of_birth_persian = serializers.SerializerMethodField(read_only=True)

    date_of_start_to_work_jalali =serializers.CharField(write_only=True,required=False,allow_null=True,allow_blank=True)
    date_of_start_to_work_persian = serializers.SerializerMethodField(read_only=True)

    contract_end_date_jalali = serializers.CharField(write_only=True,required=False,allow_null=True,allow_blank=True)
    contract_end_date_persian  = serializers.SerializerMethodField(read_only=True)

    study_category= StudyCategorySerializer(read_only=True)

    study_category_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)

    favorites = FavoriteSerializer(many=True,read_only=True)
    skills = SkillSerializer(many=True,read_only=True)
    favorite_name_list =serializers.ListField(write_only=True,required=False,allow_null=True)
    skill_name_list = serializers.ListField(write_only=True,required=False,allow_null=True)


    class Meta:
        model = WorkspaceMember
        fields = [
           "id",  "user_account", "first_name",
            "is_accepted", "permissions", "last_name", "workspace_id", "jtime", "permission_list",
            #done
            "state",
            #new begin
            "favorite_name_list",
            "skill_name_list",
            "employment_type",
            "salary_type",
            "favorites",
            "skills",
            "personal_code",
            #new end

            "city",
            "state_id",
            "folder_slug",
            "city_id",
            "insurance_type",
            "more_information",

            "is_emergency_information",
            "emergency_first_name",
            "emergency_last_name",
            "emergency_phone_number",
            "phone_number",
            "emergency_relationship",

            "email",

            "date_of_birth_jalali",
            "date_of_birth_persian",
            "national_code",
            "certificate_number",
            "gender",
            "address",
            "postal_code",
            "marriage",
            "number_of_children",
            "shaba_number",
            "education_type",
            "date_of_start_to_work_jalali",
            "date_of_start_to_work_persian",

            "contract_end_date_jalali",
            "contract_end_date_persian",
            "bad_record",
            "bad_record_id",

            "job_position",
            "study_category",
            "study_category_id",

            "military_status",
            "exempt_type",
            # not done



















        ]
    def get_date_of_birth_persian(self,obj):
        try:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.date_of_birth)
            return jalali_date.strftime('%Y/%m/%d')
        except:
            return None
    def get_date_of_start_to_work_persian(self,obj):
        try:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.date_of_start_to_work)
            return jalali_date.strftime('%Y/%m/%d')
        except:
            return None

    def get_contract_end_date_persian(self, obj):
        try:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.contract_end_date)
            return jalali_date.strftime('%Y/%m/%d')
        except:
            return None

    def create(self, validated_data):
        print(validated_data)

        from .views import create_permission_for_member
        favorite_name_list = validated_data.pop("favorite_name_list",[])
        skill_name_list = validated_data.pop("skill_name_list",[])
        employment_type = validated_data.pop("employment_type",None)
        salary_type = validated_data.pop("salary_type",None)

        folder_slug = validated_data.pop("folder_slug",None)
        workspace_id = validated_data.pop("workspace_id",None)
        bad_record_id = validated_data.pop("bad_record_id",None)
        military_status = validated_data.pop("military_status",None)
        exempt_type = validated_data.pop("exempt_type",None)
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        gender = validated_data.get("gender",None)

        workspace = get_object_or_404(WorkSpace, id=workspace_id)

        permissions = validated_data.pop("permissions",[])
        phone = validated_data.get("phone_number")
        more_information= validated_data.pop("more_information",False)
        state_id = validated_data.pop("state_id",None)
        city_id = validated_data.pop("city_id",None)
        date_of_birth_jalali = validated_data.pop("date_of_birth_jalali",None)
        date_of_start_to_work_jalali = validated_data.pop("date_of_start_to_work_jalali",None)
        contract_end_date_jalali = validated_data.pop("contract_end_date_jalali",None)
        study_category_id = validated_data.pop("study_category_id",None)
        is_emergency_information = validated_data.pop("is_emergency_information", False)
        emergency_first_name = validated_data.pop("emergency_first_name",None)
        emergency_last_name = validated_data.pop("emergency_last_name",None)
        emergency_phone_number = validated_data.pop("emergency_phone_number",None)
        emergency_relationship = validated_data.pop("emergency_relationship",None)
        user_acc, _ = UserAccount.objects.get_or_create(phone_number=phone, defaults={"is_register": False})
        if not user_acc.is_register:
            try:
                api_connection = ExternalApi(token="asdasd", headers_required=False)

                response_data = api_connection.post(
                    data={
                        "mobile": user_acc.phone_number,
                        "fullname": user_acc.fullname,
                        "avatar_url": user_acc.avatar_url(),

                    },
                    end_point="/user/auth/createBusinessUser"
                )

                user_acc.refrence_id = int(response_data['id'])
                user_acc.refrence_token = response_data['token']
            except:
                pass

        if WorkspaceMember.objects.filter(workspace=workspace, user_account=user_acc).exists() or workspace.owner == user_acc:
            raise serializers.ValidationError({
                "status": False,
                "message": "کاربر مورد نظر در حال حاظر در تیم شما وجود دارد",
                "data": {}
            })

        deleted_member = WorkspaceMember.all_objects.filter(
            is_deleted=True, workspace=workspace, user_account=user_acc
        ).first()

        if deleted_member:
            deleted_member.is_deleted = False
            deleted_member.deleted_at = None
            deleted_member.more_information=more_information
            deleted_member.first_name = validated_data.get("first_name")
            deleted_member.last_name = validated_data.get("last_name")
            deleted_member.full_name= f"{first_name} {last_name}"
            deleted_member.fullname = f"{deleted_member.first_name} {deleted_member.last_name}"
            deleted_member.is_accepted = False
            if user_acc.current_workspace_id == 0 or not WorkSpace.objects.filter(id=user_acc.current_workspace_id).exists():
                user_acc.current_workspace_id = workspace.id
                user_acc.save()

            if more_information:
                for attr, value in validated_data.items():
                    setattr(deleted_member, attr, value)
                if state_id:
                    deleted_member.state_id = state_id
                if city_id:
                    deleted_member.city_id = city_id

                if date_of_birth_jalali:
                    deleted_member.date_of_birth =persian_to_gregorian(date_of_birth_jalali)
                if date_of_start_to_work_jalali:
                    deleted_member.date_of_start_to_work = persian_to_gregorian(date_of_start_to_work_jalali)
                if contract_end_date_jalali:
                    deleted_member.contract_end_date = persian_to_gregorian(contract_end_date_jalali)


                if study_category_id:
                    deleted_member.study_category_id = study_category_id
            deleted_member.is_emergency_information = is_emergency_information
            if is_emergency_information:
                deleted_member.emergency_first_name= emergency_first_name
                deleted_member.emergency_last_name= emergency_last_name
                deleted_member.emergency_phone_number= emergency_phone_number
                deleted_member.emergency_relationship= emergency_relationship



            if gender and gender == "male":
                deleted_member.military_status = military_status
                deleted_member.exempt_type = exempt_type
            if bad_record_id:
                main_file =MainFile.objects.get(id=bad_record_id)
                main_file.its_blong=True
                main_file.save()
                deleted_member.bad_record= main_file
            if folder_slug:
                from HumanResourcesManager.models import Folder
                folder_obj = get_object_or_404(Folder,slug=folder_slug)
                folder_obj.members.add(deleted_member)
                folder_obj.save()
            for favorite in deleted_member.favorites.all():
                favorite.hard_delete()

            if favorite_name_list:
                for favorite in  favorite_name_list:
                    Favorite.objects.create(
                        title=favorite,
                        member=deleted_member

                    )
            for skill in  deleted_member.skills.all():
                skill.hard_delete()


            for skill in skill_name_list:
                Skill.objects.create(
                    title=skill,
                    member=deleted_member
                )

            if employment_type:
                deleted_member.employment_type = employment_type
            if salary_type:
                deleted_member.salary_type = salary_type
            deleted_member.save()

            return deleted_member

        member = WorkspaceMember.objects.create(**validated_data, user_account=user_acc, is_accepted=False,workspace=workspace)
        member.fullname = f"{member.first_name} {member.last_name}"
        member.more_information=more_information
        member.user_account = user_acc

        if more_information:
            if state_id:
                member.state_id = state_id
            if city_id:
                member.city_id = city_id

            if date_of_birth_jalali:
                member.date_of_birth = persian_to_gregorian(date_of_birth_jalali)
            if date_of_start_to_work_jalali:
                member.date_of_start_to_work = persian_to_gregorian(date_of_start_to_work_jalali)
            if contract_end_date_jalali:
                member.contract_end_date = persian_to_gregorian(contract_end_date_jalali)

            if study_category_id:
                member.study_category_id = study_category_id
        member.is_emergency_information = is_emergency_information
        if is_emergency_information:
            member.emergency_first_name = emergency_first_name
            member.emergency_last_name = emergency_last_name
            member.emergency_phone_number = emergency_phone_number
            member.emergency_relationship = emergency_relationship



        if gender and gender == "male":
            member.military_status = military_status
            member.exempt_type = exempt_type
        if bad_record_id:
            main_file = MainFile.objects.get(id=bad_record_id)
            main_file.its_blong = True
            main_file.save()
            member.bad_record=main_file
        if favorite_name_list:
            for favorite in favorite_name_list:
                Favorite.objects.create(
                    title=favorite,
                    member=member

                )
        for skill in skill_name_list:
            Skill.objects.create(
                title=skill,
                member=member
            )

        if employment_type:
            member.employment_type = employment_type
        if salary_type:
            member.salary_type = salary_type
        member.save()

        if not GroupMessage.objects.filter(workspace=workspace, members=workspace.owner).filter(members=user_acc).exists():
            group_message= GroupMessage.objects.create(workspace=workspace)
            group_message.members.set([workspace.owner, user_acc])

        for other in WorkspaceMember.objects.filter(workspace=workspace).exclude(id=member.id):
            if not GroupMessage.objects.filter(workspace=workspace, members=member.user_account).filter(members=other.user_account).exists():
                group_message = GroupMessage.objects.create(workspace=workspace)
                group_message.members.set([other.user_account, member.user_account])

        send_invite_link(user_acc.phone_number, workspace.owner.fullname, workspace.title)
        create_permission_for_member(member_id=member.id, permissions=permissions)

        user_acc.current_workspace_id = workspace.id
        user_acc.save()
        change_current_workspace_jadoo(user_acc=user_acc, workspace_obj=workspace)


        try:
            api_connection = ExternalApi(token=member.workspace.owner.refrence_token)

            response_data = api_connection.post(
                    data={
                        "workSpaceId": member.workspace.jadoo_workspace_id,
                        "userId": member.user_account.refrence_id,
                        "businessUserId": member.user_account.id,
                        "businessMemberId": member.id,
                    },
                    end_point="/workspace/addWorkSpaceMember"
            )
        except:
            pass

        if folder_slug:
            from HumanResourcesManager.models import Folder
            folder_obj = get_object_or_404(Folder,slug=folder_slug)
            folder_obj.members.add(member)
            folder_obj.save()
        return member

    def update(self, instance, validated_data):
        favorite_name_list = validated_data.pop("favorite_name_list", [])
        skill_name_list = validated_data.pop("skill_name_list", [])
        employment_type = validated_data.pop("employment_type", None)
        salary_type = validated_data.pop("salary_type", None)

        folder_slug = validated_data.pop("folder_slug",None)
        permissions= validated_data.pop("permissions",None)
        bad_record_id = validated_data.pop("bad_record_id", None)
        military_status = validated_data.pop("military_status", None)
        exempt_type = validated_data.pop("exempt_type", None)
        gender = validated_data.get("gender", None)
        more_information = validated_data.pop("more_information", False)
        state_id = validated_data.pop("state_id", None)
        phone= validated_data.pop("phone_number")
        city_id = validated_data.pop("city_id", None)
        date_of_birth_jalali = validated_data.pop("date_of_birth_jalali", None)
        date_of_start_to_work_jalali = validated_data.pop("date_of_start_to_work_jalali", None)
        contract_end_date_jalali = validated_data.pop("contract_end_date_jalali", None)
        study_category_id = validated_data.pop("study_category_id", None)
        is_emergency_information = validated_data.pop("is_emergency_information", False)
        emergency_first_name = validated_data.pop("emergency_first_name", None)
        emergency_last_name = validated_data.pop("emergency_last_name", None)
        emergency_phone_number = validated_data.pop("emergency_phone_number", None)
        emergency_relationship = validated_data.pop("emergency_relationship", None)
        # Update related user account data
        if phone  != instance.user_account.phone_number :
            user_acc, _ = UserAccount.objects.get_or_create(phone_number=phone, defaults={"is_register": False})
            if not user_acc.is_register:
                try:
                    url = f"{os.getenv('JADOO_BASE_URL')}/user/auth/createBusinessUser"
                    payload = {"mobile": phone, "password": "asdlaskjd","fullname":user_acc.fullname,
                    "avatar_url":user_acc.avatar_url(),}
                    response = requests.post(url=url, data=payload).json()
                    user_acc.refrence_id = int(response['data']['id'])
                    user_acc.refrence_token = response['data']['token']
                    user_acc.save()
                except:
                    pass

            if WorkspaceMember.objects.filter(workspace=instance.workspace,
                                              user_account=user_acc).exclude(id=instance.id).exists() or instance.workspace.owner == user_acc:
                raise serializers.ValidationError({
                    "status": False,
                    "message": "کاربر مورد نظر در حال حاظر در تیم شما وجود دارد",
                    "data": {}
                })

            instance.user_account = user_acc
            instance.save()
        # به‌روزرسانی مقادیر پایه
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if more_information:
            if state_id is not None:
                instance.state_id = state_id
            if city_id is not None:
                instance.city_id = city_id
            if date_of_birth_jalali:
                instance.date_of_birth = persian_to_gregorian(date_of_birth_jalali)
            if date_of_start_to_work_jalali:
                instance.date_of_start_to_work = persian_to_gregorian(date_of_start_to_work_jalali)
            if contract_end_date_jalali:
                instance.contract_end_date = persian_to_gregorian(contract_end_date_jalali)
            if study_category_id:
                instance.study_category_id = study_category_id
        instance.is_emergency_information = is_emergency_information
        if is_emergency_information:
            instance.emergency_first_name = emergency_first_name
            instance.emergency_last_name = emergency_last_name
            instance.emergency_phone_number = emergency_phone_number
            instance.emergency_relationship = emergency_relationship


        if gender and gender == "male":
            instance.military_status = military_status
            instance.exempt_type = exempt_type

        # مدیریت bad_record_id
        if bad_record_id is not None:
            if instance.bad_record:
                instance.bad_record.delete()
            main_file = MainFile.objects.get(id=bad_record_id)
            main_file.its_blong=True
            main_file.save()
            instance.bad_record=main_file
        else:
            if instance.bad_record:
                instance.bad_record.delete()

        instance.fullname = f"{instance.first_name} {instance.last_name}"
        instance.more_information= more_information

        for favorite in instance.favorites.all():
            favorite.hard_delete()

        for favorite in favorite_name_list:
                Favorite.objects.create(
                    title=favorite,
                    member=instance

                )
        for skill in instance.skills.all():
            skill.hard_delete()

        for skill in skill_name_list:
            Skill.objects.create(
                title=skill,
                member=instance
            )

        if employment_type:
            instance.employment_type = employment_type
        if salary_type:
            instance.salary_type = salary_type
        instance.save()
        if folder_slug:
            from HumanResourcesManager.models import Folder
            folder_obj = get_object_or_404(Folder, slug=folder_slug)
            folder_obj.members.add(instance)
            folder_obj.save()
        return instance




class WorkSpaceMemberMainSerializer (serializers.ModelSerializer):
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
            try:
                jadoo_base_url = os.getenv("JADOO_BASE_URL")
                # send user to jadoo

                url = f"{jadoo_base_url}/user/auth/createBusinessUser"
                payload = {
                    "mobile": user_acc.phone_number,

                    "password": "asdlaskjd",

                }
                response_data = requests.post(url=url, data=payload)
                print(response_data.json())
                recive_data = response_data.json()

                user_acc.refrence_id = int(recive_data['data']['id'])
                user_acc.refrence_token = recive_data['data']['token']
                user_acc.save()
            except:
                pass
        if WorkspaceMember.all_objects.filter(workspace=workspace_obj,user_account=user_acc).exists() or workspace_obj.owner == user_acc:

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

                item.is_accepted =False
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

