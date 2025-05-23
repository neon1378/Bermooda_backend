from MySQLdb.constants.ER import WRONG_TABLE_NAME
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers
from WorkSpaceManager.serializers import IndustrialActivitySerializer
from sqlalchemy.util import ellipses_string
from UserManager.serializers import MemberSerializer
from core.widgets import create_reminder
from .models import *
from CustomerFinance.models import Invoice, Installment
from core.serializers import CitySerializer,StateSerializer
import magic
import pandas as pd
from django.shortcuts import get_object_or_404
from core.widgets import  persian_to_gregorian
from UserManager.serializers import UserDetailSerializer
from core.serializers import StateSerializer, CitySerializer, MainFileSerializer
from MailManager.serializers import  MemberSerializer
from Notification.views import create_notification
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
    group_crm_id = serializers.IntegerField(write_only=True,required=True)
    workspace_id = serializers.IntegerField(write_only=True, required=True)
    class Meta:
        model = Category
        fields = [
            "id",
            "workspace_id",
            "title",
            "group_crm_id",
        ]
    def create(self, validated_data):
        new_category = Category.objects.create(**validated_data)
        return new_category

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title")
        instance.save()
        return instance

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
    industrial_activity_id =serializers.IntegerField(required=False,write_only=True,allow_null=True)
    industrial_activity=IndustrialActivitySerializer(read_only=True)
    city_id =serializers.IntegerField(write_only=True,required=False)
    state_id =serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = CustomerUser
        fields = [
            "user_account",
            "user_account_id",
            "is_deleted",
            "group_crm_id_main",
            "avatar_id",
            "group_crm_id",
            "avatar_url",
            "workspace_id",
            "datetime_to_remember_persian",
            "id",
            "step_status",
            "order",
            "is_deleted",
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
            "website",
            #new
            "is_followed",
            "city_id",
            "state_id",
            "category",
            "category_id",
            "phone_number_static",
            "agent_email_or_link",
            "agent_position",
            "address",
            "description",
            "app_avatar_url",
            "city",
            "state",
            "link",
            "fax",
            "gender",
            "industrial_activity",
            "industrial_activity_id",
            "manager_national_code",
            "economic_code",
            "manager_phone_number",
            "date_time_formated",
        ]
        def create(self,validated_data):
            workspace_id = validated_data.pop("workspace_id")
            avatar_id = validated_data.pop("avatar_id",None)
            industrial_activity_id=validated_data.pop("industrial_activity_id",None)
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
            date_time_to_remember=validated_data.get("date_time_to_remember",None)
            workspace_obj = WorkSpace.objects.get(id=workspace_id)

            group_crm_objs = GroupCrm.objects.filter(workspace=workspace_obj)
            for group in group_crm_objs:
                is_customer_exists =  CustomerUser.objects.filter(phone_number=phone_number,group_crm= group).exists()
                if is_customer_exists:
                    raise serializers.ValidationError(
                        {
                            "status": False,
                            "message": "شماره تلفن وارد شده در حال حاضر در کسب و کار شما وجود دارد"
                        }
                    )
            # if CustomerUser.objects.filter(group_crm__workspace=workspace_obj,phone_number=phone_number).exists():
            #     raise serializers.ValidationError(
            #         {
            #             "status":False,
            #             "message":"شماره تلفن وارد شده در حال حاضر در کسب و کار شما وجود دارد"
            #         }
            #     )
            if CustomerUser.objects.filter(group_crm__workspace=workspace_obj,email=email).exists():
                raise serializers.ValidationError(
                    {
                        "status":False,
                        "message":"ایمیل وارد شده در حال حاضر در کسب و کار شما وجود دارد"
                    }
                )
            new_customer = CustomerUser.objects.create(**validated_data)
            if industrial_activity_id:
                new_customer.industrial_activity_id=industrial_activity_id
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
            workspace_obj = WorkSpace.objects.get(id=workspace_id)
            if CustomerUser.objects.filter(group_crm__workspace=workspace_obj,phone_number=phone_number).exists() and instance.phone_number != phone_number:
                raise serializers.ValidationError(
                    {
                        "status":False,
                        "message":"شماره تلفن وارد شده در حال حاضر در کسب و کار شما وجود دارد"
                    }
                )
            if CustomerUser.objects.filter(group_crm__workspace=workspace_obj,email=email).exists() and instance.email != email:
                raise serializers.ValidationError(
                    {
                        "status":False,
                        "message":"ایمیل وارد شده در حال حاضر در کسب و کار شما وجود دارد"
                    }
                )
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

    def calculate_user_activity(self,number_of_sales: int, average_sale_value: float, number_of_followups: int) -> float:
        if number_of_followups == 0:
            return 0  # جلوگیری از تقسیم بر صفر

        # محاسبه امتیاز خام
        raw_score = (number_of_sales / number_of_followups) * average_sale_value

        # نرمال‌سازی به درصد: فرض می‌کنیم ماکزیمم امتیاز قابل انتظار 100,000 هست (قابل تنظیم بر اساس داده‌های واقعی)
        max_score = 100000
        activity_percentage = min((raw_score / max_score) * 100, 100)

        return round(activity_percentage)
    def to_representation(self, instance):
        data = super().to_representation(instance)
        workspace_obj = instance.workspace
        for member in data['members']:
            user_account = UserAccount.objects.get(id=member['id'])

            customer_users = CustomerUser.objects.filter(user_account=user_account,group_crm=instance)
            is_followed_count = customer_users.filter(is_followed=True).count()
            payed_invoices = 0
            invoice_count = 0
            for customer in customer_users:
                invoice_objs = Invoice.objects.filter(customer=customer)

                for invoice in invoice_objs:
                    if invoice.payment_type:
                        is_count = False
                        if invoice.payment_type == "cash":
                            if invoice.is_paid:
                                final_price = invoice.factor_price()
                                payed_invoices += final_price
                                invoice_count += 1

                        elif invoice.payment_type == "installment":
                            installment_invoice = Installment.objects.filter(invoice=invoice)
                            for item in installment_invoice:
                                if item.is_paid:
                                    payed_invoices += item.price

                                    is_count = True
                        if is_count:
                            invoice_count += 1

            average_member = self.calculate_user_activity(
                number_of_sales= invoice_count,
                average_sale_value = invoice_count,
                number_of_followups = is_followed_count
            )
            member['progress_average'] = average_member
        return data







    def update(self, instance, validated_data):
        title = validated_data.get("title")
        instance.title = title
        instance.save()
        return instance

class CustomerBankSerializer(serializers.ModelSerializer):
    document_id = serializers.IntegerField(write_only=True, required=True)
    state_id = serializers.IntegerField(write_only=True, required=False)
    city_id = serializers.IntegerField(write_only=True, required=False)
    main_city = CitySerializer(read_only=True)
    main_state = StateSerializer(read_only=True)

    class Meta:
        model = CustomerBank
        fields = [
            "main_city",
            "main_state",
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

        if not instance.is_local:
            if instance.main_city:
                data['city'] = instance.main_city.name
            if instance.main_state:

                data['state'] = instance.main_state.name
        return data

    def create(self, validated_data):
        main_city_id = validated_data.pop("city_id",None)
        main_state_id = validated_data.pop("state_id",None)
        new_customer_bank = CustomerBank.objects.create(**validated_data, is_local=False)
        if main_city_id:
            new_customer_bank.main_city_id = main_city_id
        if main_state_id:
            new_customer_bank.main_state_id = main_state_id
        new_customer_bank.save()
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
            instance.main_state_id = validated_data['state_id']
        if 'city_id' in validated_data:
            instance.main_city_id  = validated_data['city_id']

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
            "fullname_or_company_name":"نام مشتری/شرکت",
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






class CustomerStatusSerializer(serializers.Serializer):
    STATUS_TYPE = [
        ("dont_followed", "Dont Followed"),
        ("follow_in_another_time", "Follow In Another Time"),
        ("successful_sell", "Successful Sell"),
    ]
    CONNECTION_TYPE = [
        ("phone", "PHONE"),
        ("email", "EMAIL"),
    ]


    customer_id = serializers.IntegerField(required=True)
    customer_status = serializers.ChoiceField(choices=STATUS_TYPE, required=True)
    description = serializers.CharField(required=False, allow_blank=True,allow_null=True)
    date_time_to_remember = serializers.CharField(max_length=30, required=False, allow_blank=True,allow_null=True)
    connection_type = serializers.ChoiceField(choices=CONNECTION_TYPE, required=False, allow_blank=True,allow_null=True)
    user_account_id = serializers.IntegerField(required=False, allow_null=True)
    file_id_list = serializers.ListField(required=False, allow_null=True)
    follow_up_again = serializers.BooleanField(default=False, allow_null=True)
    invoice_id = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        user = self.context.get("user")
        customer_status = validated_data["customer_status"]
        customer_obj = get_object_or_404(CustomerUser, id=validated_data["customer_id"])
        file_id_list = validated_data.get("file_id_list",None)
        # Handle adding report if description exists
        description = validated_data.get("description")
        user_account_id= validated_data.get("user_account_id",None)
        channel_layer = get_channel_layer()

        if description:
            report = Report.objects.create(author=user, description=description)
        if file_id_list:

            if not description:

                report = Report.objects.create(author=user)

            for file_id in file_id_list:
                main_file = MainFile.objects.get(id=file_id)
                main_file.its_blong=True
                main_file.save()
                customer_obj.report.add(report)
        if customer_status == "dont_followed":
            customer_obj.customer_status = customer_status
            customer_obj.save()
            return customer_obj

        elif customer_status == "follow_in_another_time":
            customer_obj.customer_status = customer_status
            customer_obj.date_time_to_remember = validated_data.get("date_time_to_remember")
            customer_obj.main_date_time_to_remember = persian_to_gregorian(validated_data.get("date_time_to_remember"))
            customer_obj.connection_type = validated_data.get("connection_type")
            if customer_obj.user_account_id != user_account_id:
                title = "ارجاع مشتری "
                sub_title = f"مشتری {customer_obj.fullname_or_company_name} به شما ارجاع داده شد"
                create_notification(related_instance=customer_obj, workspace=customer_obj.group_crm.workspace,
                                    user=UserAccount.objects.get(id=user_account_id), title=title, sub_title=sub_title,
                                    side_type="new_task")
            customer_obj.user_account_id =user_account_id


        elif customer_status == "successful_sell":
            customer_obj.customer_status = customer_status
            customer_obj.last_selling_invoice_id = validated_data.get("invoice_id")
            if validated_data.get("follow_up_again"):
                customer_obj.is_followed = False
                customer_obj.date_time_to_remember = validated_data.get("date_time_to_remember")
                customer_obj.main_date_time_to_remember = persian_to_gregorian(validated_data.get("date_time_to_remember"))
                customer_obj.user_account_id = validated_data.get("user_account_id")

        customer_obj.save()
        if customer_obj.main_date_time_to_remember:
            sub_title = "یاد آوری وظیفه"

            title = f"وقت پیگیری  {customer_obj.fullname_or_company_name} هست "
            create_reminder(related_instance=customer_obj, remind_at=customer_obj.main_date_time_to_remember, title=title,
                            sub_title=sub_title)
        event = {
            "type": "send_data"
        }
        async_to_sync(channel_layer.group_send)(f"{customer_obj.group_crm.id}_crm", event)
        return customer_obj





class GroupCrmMessageSerializer(serializers.ModelSerializer):
    file = MainFileSerializer(read_only=True,many=True)
    file_id_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    replay = serializers.SerializerMethodField(read_only=True)
    replay_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    creator = MemberSerializer(read_only=True)
    creator_id = serializers.IntegerField(write_only=True,required=True)
    group_crm = GroupCrmSerializer(read_only=True)
    related_object = serializers.SerializerMethodField(read_only=True)
    group_crm_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model = GroupCrmMessage
        fields = [
            "id",
            "body",
            "group_crm",
            "group_crm_id",
            "message_type",
            "related_object",
            "created_at_date_persian",
            "file",
            "file_id_list",
            "replay",
            "replay_id",
            "creator",
            "creator_id",
            "created_at_persian",
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context.get("user")
        data['self'] = user == instance.creator
        return data
    def get_replay(self, obj):
        if obj.replay:
            return GroupCrmMessageSerializer(obj.replay).data
        return None
    def get_related_object(self,obj):
        if obj.related_object:
            return {
                "data_type":"customer_data",
                "data":CustomerSmallSerializer(obj.related_object).data
            }
    def create(self, validated_data):
        file_id_list = validated_data.pop("file_id_list",None)
        replay_id = validated_data.pop("replay_id",None)
        new_message = GroupCrmMessage.objects.create(**validated_data)
        if replay_id:
            new_message.replay_id = replay_id
        if file_id_list:
            main_files = MainFile.objects.filter(id__in=file_id_list)
            for main_file in main_files:
                main_file.its_belong = True
                main_file.save()
                new_message.file.add(main_file)

        new_message.save()
        return new_message

    def update(self, instance, validated_data):
        file_id_list = validated_data.pop("file_id_list", None)
        replay_id = validated_data.pop("replay_id", None)
        validated_data.pop("project_id")
        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)



        # Smart update for files
        if file_id_list is not None:
            # Current file IDs already attached to the message
            current_file_ids = set(instance.file.values_list('id', flat=True))
            # New file IDs from request
            new_file_ids = set(file_id_list)

            # Files to add
            to_add_ids = new_file_ids - current_file_ids
            # Files to remove
            to_remove_ids = current_file_ids - new_file_ids

            if to_remove_ids:
                instance.file.remove(*to_remove_ids)

            if to_add_ids:
                main_files_to_add = MainFile.objects.filter(id__in=to_add_ids)
                for main_file in main_files_to_add:
                    main_file.its_belong = True
                    main_file.save()
                    instance.file.add(main_file)

        instance.save()
        return instance
