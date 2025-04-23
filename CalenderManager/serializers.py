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

    class Meta:
        model= MeetingLabel

        fields =[
            "id",
            "title",
            "color_code",
            "icon",
            "titleTr1",
            "key_name",
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

    meeting_phone_numbers = MeetingPhoneNumberSerializer(many=True,read_only=True)
    meeting_emails = MeetingEmailSerializer(many=True,read_only=True)
    members = MeetingMemberSerializer(many=True,read_only=True)
    files= MainFileSerializer(many=True,read_only=True)
    workspace_id= serializers.IntegerField(required=True)

    file_id_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    member_id_list = serializers.ListField(write_only=True,required=False,allow_null=True,allow_empty=True)
    phone_number_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    email_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    label_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    date_to_start_persian = serializers.CharField(write_only=True,required=True)
    class Meta:
        model = Meeting
        fields =[
            "id",
            "label",

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

            "file_id_list",
            "member_id_list",
            "phone_number_list",
            "email_list",
            "label_id",
            "date_to_start_persian",
            "start_meeting_time",
            "end_meeting_time",

        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['user']
        owner_member = instance.members.filter(user_type="owner",user=user).first()
        if owner_member.user == user:
            data['self'] = True
        else:
            data['self'] = False
        return data
    def create(self, validated_data):
        user = self.context['user']
        hashtag_list = validated_data.pop("hashtag_list",[])
        file_id_list = validated_data.pop("file_id_list",None)
        member_id_list = validated_data.pop("member_id_list",[])
        phone_number_list = validated_data.pop("phone_number_list",[])
        email_list = validated_data.pop("email_list",[])
        label_id = validated_data.pop("label_id",None)
        date_to_start_persian= validated_data.pop("date_to_start_persian")
        remember_number = validated_data.pop("remember_number",None)
        new_meeting  = Meeting.objects.create(**validated_data)
        new_meeting.date_to_start= persian_to_gregorian(date_to_start_persian)

        if label_id:
            new_meeting.label_id=label_id
        if remember_number:
            new_meeting.remember_number=remember_number
        try:
            for file_id in file_id_list:
                main_file= MainFile.objects.get(id=file_id)
                main_file.its_blong=True
                new_meeting.files.add(main_file)
        except:
            pass

        if phone_number_list:
            for phone in phone_number_list:
                MeetingPhoneNumber.objects.create(
                    phone_number=phone,
                    meeting=new_meeting
                )
        if email_list:
            for email in email_list:
                MeetingEmail.objects.create(
                    email =email,
                    meeting=new_meeting
                )
        if member_id_list:
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
        new_meeting.save()
        return new_meeting

    def update(self, instance, validated_data):
        hashtag_list = validated_data.pop("hashtag_list", None)
        file_id_list = validated_data.pop("file_id_list", None)
        member_id_list = validated_data.pop("member_id_list", None)
        phone_number_list = validated_data.pop("phone_number_list", None)
        email_list = validated_data.pop("email_list", None)
        label_id = validated_data.pop("label_id", None)
        date_to_start_persian = validated_data.pop("date_to_start_persian", None)
        remember_number = validated_data.pop("remember_number", None)

        # Update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if date_to_start_persian:
            instance.date_to_start = persian_to_gregorian(date_to_start_persian)

        if label_id is not None:
            instance.label_id = label_id

        if remember_number is not None:
            instance.remember_number = remember_number

        instance.save()

        # === Update files ===
        if file_id_list is not None:
            current_file_ids = set(instance.files.values_list("id", flat=True))
            new_file_ids = set(file_id_list)

            to_remove_ids = current_file_ids - new_file_ids
            if to_remove_ids:
                instance.files.remove(*to_remove_ids)

            to_add_ids = new_file_ids - current_file_ids
            for file_id in to_add_ids:
                main_file = MainFile.objects.get(id=file_id)
                main_file.its_blong = True
                main_file.save()
                instance.files.add(main_file)


        # === Update phone numbers ===
        if phone_number_list is not None:
            current_phones = set(instance.meeting_phone_numbers.values_list("phone_number", flat=True))
            new_phones = set(phone_number_list)

            instance.meeting_phone_numbers.filter(phone_number__in=(current_phones - new_phones)).delete()
            for phone in new_phones - current_phones:
                MeetingPhoneNumber.objects.create(phone_number=phone, meeting=instance)

        # === Update emails ===
        if email_list is not None:
            current_emails = set(instance.meeting_emails.values_list("email", flat=True))
            new_emails = set(email_list)

            instance.meeting_emails.filter(email__in=(current_emails - new_emails)).delete()
            for email in new_emails - current_emails:
                MeetingEmail.objects.create(email=email, meeting=instance)

        # === Update members (only user_type="member") ===
        if member_id_list is not None:
            user = self.context["user"]
            current_member_ids = set(
                instance.members.filter(user_type="member").values_list("user_id", flat=True)
            )
            new_member_ids = set(member_id_list) - {user.id}

            members_to_remove = current_member_ids - new_member_ids
            if members_to_remove:
                instance.members.filter(user_type="member", user_id__in=members_to_remove).delete()

            members_to_add = new_member_ids - current_member_ids
            for member_id in members_to_add:
                MeetingMember.objects.create(
                    user_type="member",
                    user_id=member_id,
                    meeting=instance
                )

        return instance
