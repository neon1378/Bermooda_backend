from distutils.dep_util import newer_group

from rest_framework import serializers
from .models import  *
from MailManager.serializers import MemberSerializer
from core.serializers import MainFileSerializer
from core.widgets import persian_to_gregorian
from core.models import MainFile
class MeetingHashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingHashtag
        fields=[
            "id",
            "name"
        ]


class MeetingPhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model= MeetingPhoneNumber
        fields =[
            "id",
            "phone_number",

        ]

class MeetingEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingEmail
        fields =[
            "id",
            "email",

        ]

class MeetingMemberSerializer(serializers.ModelSerializer):
    user = MemberSerializer(read_only=True)
    class Meta:
        model = MeetingMember
        fields = [
            "id",
            "user_type",
            "user",


        ]


class MeetingLabelSerializer(serializers.ModelSerializer):
    workspace_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model= MeetingLabel

        fields =[
            "id",
            "workspace_id",
            "title",
            "color_code"
        ]
    def create(self, validated_data):
        new_label = MeetingLabel.objects.create(**validated_data)
        return new_label
    def update(self, instance, validated_data):
        instance.title = validated_data.get("title")
        instance.color_code = validated_data.get("color_code")
        instance.save()
        return instance


class MeetingSerializer(serializers.ModelSerializer):
    label = MeetingLabelSerializer(read_only=True)
    meeting_hashtags =  MeetingHashtagSerializer(many=True,read_only=True)
    meeting_phone_numbers = MeetingPhoneNumberSerializer(many=True,read_only=True)
    meeting_emails = MeetingEmailSerializer(many=True,read_only=True)
    members = MeetingMemberSerializer(many=True,read_only=True)
    files= MainFileSerializer(many=True,read_only=True)
    workspace_id= serializers.IntegerField(required=True)
    hashtag_list = serializers.ListField(write_only=True,allow_null=True)
    file_id_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    member_id_list = serializers.ListField(write_only=True,required=True)
    phone_number_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    email_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    label_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    date_to_start_persian = serializers.CharField(write_only=True,required=True)
    class Meta:
        model = Meeting
        fields =[
            "id",
            "label",
            "meeting_hashtags",
            "meeting_phone_numbers",
            "meeting_emails",
            "workspace_id",
            "members",

            "reaped_type",
            "files",
            "date_to_start",
            "title",
            "remember_type",
            "remember_number",
            "description",
            "more_information",
            "link",
            # fields
            "hashtag_list",
            "file_id_list",
            "member_id_list",
            "phone_number_list",
            "email_list",
            "label_id",
            "date_to_start_persian",
            "start_meeting_time",
            "end_meeting_time",

        ]
    def create(self, validated_data):
        user = self.context['user']
        hashtag_list = validated_data.pop("hashtag_list",[])
        file_id_list = validated_data.pop("file_id_list",[])
        member_id_list = validated_data.pop("member_id_list",[])
        phone_number_list = validated_data.pop("phone_number_list",[])
        email_list = validated_data.pop("email_list",[])
        label_id = validated_data.pop("label_id",None)
        date_to_start_persian= validated_data.pop("date_to_start_persian")
        new_meeting  = Meeting.objects.create(**validated_data)
        new_meeting.date_to_start= persian_to_gregorian(date_to_start_persian)

        if label_id:
            new_meeting.label_id=label_id
        for file_id in file_id_list:
            main_file= MainFile.objects.get(id=file_id)
            main_file.its_blong=True
            new_meeting.files.add(main_file)

        new_meeting.save()
        for hashtag in hashtag_list:
            MeetingHashtag.objects.create(
                name = hashtag,
                meeting= new_meeting
            )
        for phone in phone_number_list:
            MeetingPhoneNumber.objects.create(
                phone_number=phone,
                meeting=new_meeting
            )
        for email in email_list:
            MeetingEmail.objects.create(
                email =email,
                meeting=new_meeting
            )
        for member in member_id_list:
            if member != user.id:
                MeetingMember.objects.create(
                    user_type ="member",
                    user_id=member,
                    meeting = new_meeting
                )

        MeetingMember.objects.create(
            user_type="owner",
            user=user,
            meeting=new_meeting
        )
        return new_meeting
