from rest_framework import serializers
from .models import *
from CrmCore.models import *
from core.models import City,State
from WorkSpaceManager.models import WorkspaceMember
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = [
            "id",
            "fullname",
            "avatar_url"
        ]



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
  
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields =[
            "id",
            "full_name",
            "avatar_url"
        ]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "description"
            
        ]

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id","name"]

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["id","name"]




class UserAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAccount
        fields = [
            "fullname",
            "phone_number",
            "id"


     

        ]   

    def create(self, validated_data):



        # Create the new UserAccount
        new_user_acc = UserAccount(
            **validated_data,
    
        )

        new_user_acc.save()

        return new_user_acc
            


    





class UserAccountSerializerShow(serializers.ModelSerializer):

    class Meta:
        model = UserAccount
        fields = [
       
            "username",
            "personal_type",
 
            "phone_number",

            "email",
  
            "city_name",
            "state_name",

            "id"
        ]





    



class ReadyTextSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(write_only=True,required=False)
    workspace_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:

        model = ReadyText
        fields = [
            "id",
            "text",
            "owner_id",
            "workspace_id",

        ]



    def create (self,validated_data):
        print(validated_data)
        new_ready_text = ReadyText.objects.create(**validated_data)

        return new_ready_text
    
    def update(self, instance, validated_data):
        instance.text=validated_data.get("text")
        instance.save()
        return instance





