from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from jdatetime import datetime, timedelta
from MailManager.serializers import MemberSerializer,FileDetail



class HashtagSerializer(ModelSerializer):
    class Meta:
        model = Hashtag
        fields =[
            "id",
            "name"
        ]

class PhoneNumberSerializer(ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields =[
            "id",
            "phone_number"
        ]

class EmailSerializer(ModelSerializer):
    class Meta:
        model = Email
        fields =[
            "id",
            "email"
        ]


class InviterUserSerializer(ModelSerializer):
    user = MemberSerializer(read_only=True)
    class Meta:
        model = InvitedUser
        fields = [
            "id",
            "user"

        ]

class PlaningSerializer(ModelSerializer):
    hashtags = HashtagSerializer(read_only=True,many=True)
    files =FileDetail(read_only=True,many=True)
    email_list = serializers.ListField(write_only=True,required=False)
    phone_number_list = serializers.ListField(write_only=True,required=False)
    phone_numbers = PhoneNumberSerializer(read_only=True,many=True)
    emails = EmailSerializer(read_only=True,many=True)
    creator = MemberSerializer(read_only=True)
    hashtag_list = serializers.ListField(write_only=True,required=False)
    workspace_id = serializers.IntegerField(write_only=True,required=True)
    creator_id = serializers.IntegerField(write_only=True,required=False)
    invited_userss = serializers.ListField(write_only=True,required=False)
    invited_users= InviterUserSerializer(many=True,read_only=True)
    reaped_type =  serializers.CharField(write_only =True,required=False)
    file_id_list = serializers.ListField(write_only=True,required=False)
    class Meta:
        model = Planing
        fields = [
            "files",
            "file_id_list",
            "remember_type",
            "invited_users",
            "email_list",
            "phone_number_list",
            "phone_numbers",
            "emails",
            "invited_userss",
            "workspace_id",
            "creator_id",
            "hashtag_list",
            "hashtags",
            "date_in_calender",
            "label_title",
            "label_color_code",
            "title",
            "creator",
            "remember_date",
            "reaped_status",
            "reaped_type_current",
            "description",
            "more_information",
            "date_to_start",
            "date_to_end",
            "link",
            "reaped_type"
        ]
    def create(self, validated_data):
        creator_id=validated_data.get("creator_id",None)
        file_id_list = validated_data.pop("file_id_list",[])
        hashtag_list = validated_data.pop("hashtag_list",[])
        invited_users= validated_data.pop("invited_userss",[])
        date_to_start = validated_data.pop("date_to_start",None)
        date_to_end = validated_data.pop("date_to_end",None)
        link = validated_data.pop("link",None)
        reaped_type= validated_data.pop("reaped_type",None)
        email_list =validated_data.pop("email_list",None)
        remember_date = validated_data.pop("remember_date",None)
        remember_type = validated_data.pop("remember_type",None)
        phone_number_list = validated_data.pop("phone_number_list",None)
        new_planing = Planing.objects.create(**validated_data)
        new_planing.date_to_start=date_to_start
        new_planing.date_to_end=date_to_end
        new_planing.save()
        for hashtag in hashtag_list:
            Hashtag.objects.create(
                name=hashtag,
                planing=new_planing
            )
        if new_planing.more_information:
            validated_data.pop("creator_id")

            new_planing.link=link
            if remember_type:
                new_planing.remember_date= remember_date
                new_planing.remember_type=remember_type
            new_planing.save()
            for user in invited_users:
                    if creator_id != user:
                        new_invited_user= InvitedUser.objects.create(
                            user_id= user,
                            planing= new_planing,
                            activated= False
                        )
            for email in email_list:
                    Email.objects.create(
                        email=email,
                        planing= new_planing
                    )
            for phone in phone_number_list:
                    PhoneNumber.objects.create(
                        phone_number =phone,
                        planing = new_planing
                    )
            if new_planing.reaped_status:
    
                new_range_date = RangeDateCalender.objects.create(
                        
                        start_date=new_planing.date_in_calender,
                        reaped_type = reaped_type, 
                )
                new_planing.range_date=new_range_date
                new_planing.save()

                    
  




        for file_id in file_id_list:
            main_file = MainFile.objects.get(id=file_id)
            main_file.its_blong=True
            main_file.save()
            new_planing.files.add(main_file)
        return new_planing

    




    def update(self, instance, validated_data):
        # Handle related fields to be updated
        file_id_list = validated_data.pop("file_id_list",[])
        hashtag_list = validated_data.pop("hashtag_list", [])
        invited_users = validated_data.pop("invited_userss", [])
        email_list = validated_data.pop("email_list", [])
        phone_number_list = validated_data.pop("phone_number_list", [])
        date_to_start = validated_data.pop("date_to_start", None)
        date_to_end = validated_data.pop("date_to_end", None)
        link = validated_data.pop("link", None)
        reaped_type = validated_data.pop("reaped_type", None)
        creator_id=validated_data.pop("creator_id",None)
        print()
        # Update the main fields of the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.date_to_start = date_to_start
        instance.date_to_end = date_to_end
        instance.save()

        # Update or recreate hashtags
        instance.hashtags.all().delete()
        for hashtag in hashtag_list:
            Hashtag.objects.create(name=hashtag, planing=instance)

        # Handle reaped status and related logic
        if instance.reaped_status:
            if not instance.range_date:
                new_range_date = RangeDateCalender.objects.create(
                    start_date=instance.date_in_calender,
                    reaped_type=reaped_type
                )
                instance.range_date = new_range_date
            else:
                
                instance.range_date.reaped_type = reaped_type
                instance.range_date.save()
            instance.save()

        if instance.more_information:
            # Update emails
            instance.emails.all().delete()
            for email in email_list:
                Email.objects.create(email=email, planing=instance)

            # Update phone numbers
            instance.phone_numbers.all().delete()
            for phone in phone_number_list:
                PhoneNumber.objects.create(phone_number=phone, planing=instance)

            # Update other fields

            instance.link = link
            instance.save()

            
            # Update invited users
            # for user in invited_users
            existing_users_ids = list(instance.invited_users.values_list("user_id", flat=True))

            for user in invited_users:
                if not InvitedUser.objects.filter(user_id=user,planing=instance).exists():

                    
                    InvitedUser.objects.create(
                        user_id=user,
                        planing=instance,
                        activated=False
                    )
  
            removed_user_ids = set(existing_users_ids) - set(invited_users)
            
            for user in removed_user_ids:
            
                invited_user = InvitedUser.objects.get(user_id=user,planing=instance)
                invited_user.delete()
        existing_file_ids = list(instance.files.values_list("id", flat=True))

        if file_id_list != []:  

            for file_id in file_id_list:
                main_file = MainFile.objects.get(id=file_id)
                main_file.its_blong = True
                    # instance.files.add(main_file)
            instance.files.set(file_id_list)
            removed_file_ids = set(existing_file_ids) - set(file_id_list)

            for file_id in removed_file_ids:
                main_file = MainFile.objects.get(id=file_id)
                main_file.delete()
            for file_id in instance.files.all():
                main_file = MainFile.objects.get(id=file_id)
                main_file.its_blong=True
                main_file.save()
        else: 

            for file_id in existing_file_ids:
                main_file = MainFile.objects.get(id=file_id)
                main_file.delete()
            instance.files.clear()

            
        return instance


    def get_days_in_month(self,year, month):

        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1


        first_day_next_month = datetime(next_year, next_month, 1)


        last_day_current_month = first_day_next_month - timedelta(days=1)
        return last_day_current_month.day

