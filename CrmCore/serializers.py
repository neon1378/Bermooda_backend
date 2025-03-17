from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers
from sqlalchemy.util import ellipses_string

from .models import *
import magic
import pandas as pd
from django.shortcuts import get_object_or_404
from core.widgets import  persian_to_gregorian
from UserManager.serializers import UserDetailSerializer
from core.serializers import StateSerializer, CitySerializer, MainFileSerializer
from MailManager.serializers import  MemberSerializer
class CrmDepartmentSerializer(serializers.ModelSerializer):
    workspace_id = serializers.IntegerField(write_only=True,required=True)
    manager_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model= CrmDepartment
        fields=[
            "id",
            "title",
            "workspace_id",
            "manager_id",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class LabelStepSerializer(serializers.ModelSerializer):
    label_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model= Step
        fields =[
            "id",
            "title",
            "step",
            "label_id",
        ]
    def create(self, validated_data):
        label_id = validated_data.pop("label_id")
        label_obj = get_object_or_404(Label,id=label_id)
        title = validated_data.get("title")

        last_step_obj = label_obj.label_step.steps.all().order_by("step").last()
        new_step_obj = Step.objects.create(
            title =title,
            step = last_step_obj.step +1,
            label_step= label_obj.label_step
        )
        return new_step_obj



    def update(self, instance, validated_data):
        instance.title = validated_data.get("title")
        instance.save()
        return instance

class LabelStepRelSerializer(serializers.ModelSerializer):
    steps = LabelStepSerializer(many=True)
    class Meta:
        model = LabelStep
        fields =[
            "id",
            "steps"
        ]
class LabelSerializer(serializers.ModelSerializer):
    label_step = LabelStepRelSerializer(read_only=True)
    group_crm_id = serializers.IntegerField(write_only=True,required=False)
    step_list = serializers.ListField(write_only=True,required=False)
    class Meta:
        
        model = Label
        fields = [
            "id",
            "title",
            "color",
            "label_step",
            "group_crm_id",
            "step_list",
        ]
    def create(self, validated_data):
        step_list = validated_data.pop("step_list")
        group_crm_id = validated_data.pop("group_crm_id")
        group_obj = get_object_or_404(GroupCrm,id=group_crm_id)
        new_label = Label.objects.create(**validated_data)
        new_label.group_crm = group_obj

        label_step = LabelStep.objects.create(label=new_label)
        label_step.save()

        if len(step_list) <2 or len(step_list) > 5:
            raise serializers.ValidationError(
                {
                    "status":False,
                    "message":"مراحل نباید بیشتر از ۵ پ کمتر از ۲ آیتم باشند",
                    "data":{}
                }
            )
        count_step = 1
        for step_data in step_list:
            new_step_obj = Step.objects.create(
                title = step_data,
                step =count_step ,
                label_step = label_step,
            )
            count_step+=1
        new_label.save()
        return new_label
    def update(self, instance, validated_data):
        instance.title = validated_data.get("title")
        instance.color = validated_data.get("color")
        instance.save()
        return instance












class CustomerSerializer(serializers.ModelSerializer):
  
    category = CategorySerializer()
    class Meta:
        model = CustomerUser
        fields = [

            "id",
           
            "category",

            "description",
       
            "agent_position",
            "address",
            "fullname_or_company_name",
            "personal_type",
            "state",
            "city",
            "city_name",
            "state_name",
            "email",
            "avatar_url",
            "phone_number",
            "phone_number_static",
            "website",
            "legal_information",
            "fax",
            "manager_national_code",
            "economic_code",
            "manager_phone_number",
            "agent_status",
            "agent_name",
            "agent_email_or_link",
            "agent_phone_number",
        ]
    def create (validated_data):

        category_id = validated_data.pop("category",{})
        

        city= validated_data.pop("city",None)
        state = validated_data.pop("state",None)
      
        label= validated_data.pop("label")
        new_customer = CustomerUser(**validated_data,label_id=label['id'],)

        if category_id and category_id != {}:
            category_obj = get_object_or_404(Category,id=category_id['id'])
            category=category_obj
        if state:
            new_customer.state_id=state
            new_customer.city_id=city
        new_customer.save()
        return new_customer

    def update(self, instance, validated_data):
        print(validated_data)

  
        
        category_data = validated_data.pop("category", None)

        city_id = validated_data.pop("city", None)
        state_id = validated_data.pop("state", None)


        if city_id:
            instance.city_id = city_id
        if state_id:
            instance.state_id = state_id

        
            


        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    



class CustomerSmallSerializer(serializers.ModelSerializer):
    label_id = serializers.IntegerField(write_only=True,required=True)
    user_account_id =serializers.IntegerField(write_only=True,required=True)
    group_crm_id = serializers.IntegerField(write_only=True,required=True)
    workspace_id = serializers.IntegerField(write_only=True,required=True)
    label = LabelSerializer(read_only=True)
    user_account = MemberSerializer(read_only=True)

    avatar_id = serializers.CharField(max_length=55,write_only=True,required=False)
    category = CategorySerializer(read_only=True,required=False)
    category_id = serializers.IntegerField(write_only=True,required=False)
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city_id =serializers.IntegerField(write_only=True,required=False)
    state_id =serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = CustomerUser
        fields = [
            "user_account",
            "user_account_id",
            "is_deleted",
            "avatar_id",
            "group_crm_id",
            "avatar_url",
            "workspace_id",
            "id",
            "step_status",
            "order",
            "label",
            "label_id",
            "personal_type",
            "fullname_or_company_name",
            "conection_type",
            "phone_number",
            "email",
            "date_time_to_remember",
            "agent_status",
            "agent_name",
            "agent_phone_number",

            #new
            "city_id",
            "state_id",
            "category",
            "category_id",
            "phone_number_static",
            "agent_email_or_link",
            "agent_position",
            "address",
            "description",

            "city",
            "state",
            "link",
            "fax",
            "manager_national_code",
            "economic_code",
            "manager_phone_number",
            "date_time_formated",
        ]
        def create(self,validated_data):
            workspace_id = validated_data.pop("workspace_id")
            avatar_id = validated_data.pop("avatar_id",None)
            city_id =validated_data.pop("city_id",None)
            state_id =validated_data.pop("state_id",None)
            agent_email_or_link=validated_data.pop("agent_email_or_link",None)
            agent_position=validated_data.pop("agent_position",None)
            agent_status = validated_data.pop("agent_status",False)
            agent_name = validated_data.pop("agent_name",None)
            agent_phone_number = validated_data.pop("agent_phone_number",None)
            conection_type = validated_data.pop("conection_type","phone")
            phone_number = validated_data.pop("phone_number",None)
            email = validated_data.pop("email",None)
            new_customer = CustomerUser.objects.create(**validated_data)
            if avatar_id :
                main_file = MainFile.objects.get(id=avatar_id)
                main_file.its_blong =True
                main_file.save()
                new_customer.avatar = main_file
            if city_id:
                new_customer.city_id=city_id
            if state_id :
                new_customer.state_id=state_id

            if agent_status:
                new_customer.agent_status = True
                new_customer.agent_name = agent_name
                new_customer.agent_email_or_link = agent_email_or_link
                new_customer.agent_position = agent_position

                new_customer.agent_phone_number= agent_phone_number



            if conection_type == "phone":
                new_customer.connection_type =conection_type
                new_customer.phone_number = phone_number
            else:
                new_customer.connection_type = "email"
                new_customer.email = email
            new_customer.main_date_time_to_remember = persian_to_gregorian(new_customer.date_time_to_remember)

            new_customer.save()
            channel_layer = get_channel_layer()
            event = {
                "type": "send_data"
            }
            async_to_sync(channel_layer.group_send)(f"{new_customer.group_crm.id}_crm", event)

            return new_customer

        def update(self, instance, validated_data):
            workspace_id = validated_data.pop("workspace_id")
            avatar_id = validated_data.pop("avatar_id", None)
            city_id = validated_data.pop("city_id", None)
            state_id = validated_data.pop("state_id", None)
            agent_email_or_link = validated_data.pop("agent_email_or_link", None)
            agent_position = validated_data.pop("agent_position", None)
            agent_status = validated_data.pop("agent_status", None)
            agent_name = validated_data.pop("agent_name", None)
            agent_phone_number = validated_data.pop("agent_phone_number", None)
            conection_type = validated_data.pop("conection_type", None)
            phone_number = validated_data.pop("phone_number", None)
            email = validated_data.pop("email", None)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if avatar_id:
                if avatar_id != instance.avatar.id:
                    instance.avatar.delete()
                    main_file = MainFile.objects.get(id=avatar_id)
                    main_file.its_blong = True
                    main_file.save()
                    instance.avatar = main_file
            print(conection_type)
            if city_id:
                instance.city_id = city_id
            if state_id:
                instance.state_id = state_id

            if agent_status is not None:
                instance.agent_status = agent_status
                instance.agent_name = agent_name
                instance.agent_email_or_link = agent_email_or_link
                instance.agent_position = agent_position
                instance.agent_phone_number = agent_phone_number

            # if conection_type:
            instance.connection_type = conection_type
            if conection_type == "phone":
                instance.phone_number = phone_number
            else:
                instance.email = email
            instance.main_date_time_to_remember = persian_to_gregorian(instance.date_time_to_remember)
            instance.save()
            channel_layer = get_channel_layer()
            event = {"type": "send_data"}
            async_to_sync(channel_layer.group_send)(f"{instance.group_crm.id}_crm", event)

            return instance

class CampaignFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model= CampaignField
        fields = [
            "id",
            "title",
            "field_type",
        ]
class CampaignSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField(write_only=True,required=False)
    group_crm_id = serializers.IntegerField(write_only=True,required=True)
    creator_id = serializers.IntegerField(write_only=True,required=True)
    creator= MemberSerializer(read_only=True)
    field_list = serializers.ListField(write_only=True,required=False)
    fields = CampaignFieldSerializer(read_only=True,many=True)
    class Meta:
        model= Campaign
        fields = [
            "id",
            "creator",
            "uuid",
            "fields",
            "image_id",
            "image_url",
            "group_crm_id",
            "creator_id",
            "title",
            "description",
            "field_list",

            "jtime",
        ]
    def create(self, validated_data):
        field_list= validated_data.pop("field_list",[])
        image_id = validated_data.pop("image_id",None)
        new_campaign= Campaign.objects.create(**validated_data)
        if image_id:
            main_file= MainFile.objects.get(id=image_id)
            main_file.its_blong=True
            main_file.save()
            new_campaign.image= main_file
        for field in field_list:
            new_field = CampaignField(
                field_type=field['field_type'],
                title= field['title'],
                campaign = new_campaign
            )
            new_field.save()

        new_campaign.save()
        return new_campaign
    def update(self, instance, validated_data):

        image_id = validated_data.pop("image_id",None)
        group_crm_id = validated_data.pop("group_crm_id")
        creator_id = validated_data.pop("creator_id")
        instance.title = validated_data.get("title")
        instance.description = validated_data.get("description")

        if image_id:
            if image_id != instance.image.id:
                instance.image.delete()
                main_file= MainFile.objects.get(id=image_id)
                main_file.its_blong=True
                main_file.save()
                instance.image = main_file

        instance.save()
        return instance


class CampaignFormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignFormData
        fields = [
            "field_type",
            "id",
            "title",
            "text",
        ]
class CampaignFormSerializer(serializers.ModelSerializer):
    form_data= CampaignFormDataSerializer(read_only=True,many=True)
    class Meta:
        model = CampaignForm
        fields = [

            "id",
            "form_data",
            "fullname",
        ]



class GroupCrmSerializer(serializers.ModelSerializer):
    members= MemberSerializer(many=True,read_only=True)
    department = CrmDepartmentSerializer(read_only=True)
    class Meta:
        model = GroupCrm
        fields =[
            "id",
            "title",
            "avatar_url",
            "members",
            "profit_price",
            "department",
            "summery_customers",

        ]



    def update(self, instance, validated_data):
        title = validated_data.get("title")
        instance.title = title
        instance.save()
        return instance

class CustomerBankSerializer(serializers.ModelSerializer):
    document_id = serializers.IntegerField(write_only=True, required=True)
    state_id = serializers.IntegerField(write_only=True, required=False)
    city_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = CustomerBank
        fields = [
            "id",
            "state_id",
            "city_id",
            "document_id",
            "phone_number",
            "state",
            "city",
            "static_phone_number",
            "address",
            "email",
            "fullname_or_company_name",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.is_local:
            data['city'] = instance.main_city.name
            data['state'] = instance.main_state.name
        return data

    def create(self, validated_data):
        new_customer_bank = CustomerBank.objects.create(**validated_data, is_local=True)
        return new_customer_bank

    def update(self, instance, validated_data):
        # Update instance fields dynamically based on provided data
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.static_phone_number = validated_data.get('static_phone_number', instance.static_phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.email = validated_data.get('email', instance.email)
        instance.fullname_or_company_name = validated_data.get('fullname_or_company_name', instance.fullname_or_company_name)

        # Handle state and city updates
        if 'state_id' in validated_data:
            instance.state_id = validated_data['state_id']
        if 'city_id' in validated_data:
            instance.city_id = validated_data['city_id']

        instance.save()
        return instance




class CustomerDocumentSerializer(serializers.ModelSerializer):
    exel_file = MainFileSerializer(read_only=True)
    exel_file_id = serializers.IntegerField(write_only=True, required=True)
    group_crm_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = CustomerDocument
        fields = ["id", "exel_file", "exel_file_id","group_crm_id"]

    def create(self, validated_data):
        exel_file_id = validated_data.pop("exel_file_id")
        main_file_obj = get_object_or_404(MainFile, id=exel_file_id)

        # Check MIME type
        mime = magic.Magic(mime=True)
        file_mime_type = mime.from_buffer(main_file_obj.file.read(2048))
        if file_mime_type not in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX
            "application/vnd.ms-excel",  # XLS
        ]:
            raise serializers.ValidationError(
                {"status": False, "message": "فرمت فایل ارسال شده Excel نمی‌باشد"}
            )
        main_file_obj.file.seek(0)  # Reset file pointer only if validation passed
        main_file_obj.its_blong = True
        main_file_obj.save()

        # Create CustomerDocument instance
        new_customer_document = CustomerDocument.objects.create(**validated_data)
        new_customer_document.exel_file = main_file_obj
        new_customer_document.save()
        # Read the Excel file
        df = pd.read_excel(main_file_obj.file.path)

        # Define expected columns
        column_mapping = {
            "phone_number": "شماره تماس",
            "static_phone_number": "شماره ثابت",
            "state": "استان",
            "city": "شهر",
            "address": "آدرس",
            "email": "ایمیل",
        }

        # Process rows and save data
        for _, row in df.iterrows():
            new_customer = CustomerBank(document=new_customer_document)
            for field, column_name in column_mapping.items():
                if column_name in df.columns and not pd.isna(row[column_name]):
                    setattr(new_customer, field, row[column_name])

            new_customer.save()

        return new_customer_document