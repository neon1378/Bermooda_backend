from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
from UserManager.serializers import UserDetailSerializer

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


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        
        model = Label
        fields = [
            "id",
            "title",
            "color",
        ]











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
    avatar_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = CustomerUser
        fields = [
            "user_account_id",
            "avatar_id",
            "group_crm_id",
            "avatar_url",
            "workspace_id",
            "id",
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

        ]
        def create(self,validated_data):
            workspace_id = validated_data.pop("workspace_id")
            avatar_id = validated_data.pop("avatar_id",0)
            agent_status = validated_data.pop("agent_status",False)
            agent_name = validated_data.pop("agent_name",None)
            agent_phone_number = validated_data.pop("agent_phone_number",None)
            conection_type = validated_data.pop("conection_type","phone")
            phone_number = validated_data.pop("phone_number",None)
            email = validated_data.pop("email",None)
            new_customer = CustomerUser.objects.create(**validated_data)
            if avatar_id and int(avatar_id) != 0:
                main_file = MainFile.objects.get(id=avatar_id)
                main_file.its_blong =True
                main_file.save()
                new_customer.avatar = main_file

            if agent_status:
                new_customer.agent_status = True
                new_customer.agent_name = agent_name
                new_customer.agent_phone_number= agent_phone_number


            if conection_type == "phone":
                new_customer.connection_type =conection_type
                new_customer.phone_number = phone_number
            else:
                new_customer.connection_type = conection_type
                new_customer.email = email

            new_customer.save()
            return new_customer
