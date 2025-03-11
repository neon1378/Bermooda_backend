from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from UserManager.models import UserAccount
from django.shortcuts import get_object_or_404
from core.models import MainFile
from core.serializers import  MainFileSerializer
class MemberSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        fields = [
            "id",
            "fullname",
            "avatar_url"
        ]

class MailStatusSerializer(ModelSerializer):
    class Meta:
        model= MailStatus
        fields ="__all__"
class FileDetail(ModelSerializer):

    class Meta:
        model= MainFile
        fields = [
            "id",
            "file_url",

        ]


class MailReportSerializer(ModelSerializer):
    file_id_list = serializers.ListField(write_only=True,required=False)
    creator_id = serializers.IntegerField(write_only=True)
    creator = MemberSerializer(read_only=True)
    mail_id = serializers.IntegerField(write_only=True)
    class Meta:
        model= MailReport
        fields =[
            'mail_id',
            'creator',
            'id',
            "creator_id",
            'text',
            'file_urls',
            'jtime',
            'file_id_list'
        ]
    def create(self, validated_data):
        file_id_list = validated_data.pop('file_id_list',[])
        new_mail_report = MailReport.objects.create(**validated_data)
        for file_id in file_id_list:
            main_file = MainFile.objects.get(id=file_id)
            main_file.its_blong=True
            main_file.save()
            new_mail_report.files.add(file_id)

        return new_mail_report

class SignatureMailSerializer(ModelSerializer):
    owner= MemberSerializer(read_only=True)
    signature= FileDetail(read_only=True)
    class Meta:
        model = SignatureMail
        fields =[
            "id",
            "owner",
            "sign_status",
            "signature",
            "order"
        ]

class MaliLabelSerializer(ModelSerializer):
    workspace_id = serializers.IntegerField(write_only=True)

    class Meta:

        model = MailLabel
        fields = [
            "workspace_id",
            "id",
            "title",
            "color_code"
        ]

class MailRecipientSerializer(ModelSerializer):
    user = MemberSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True,required=True)
    signature_image = MainFileSerializer(read_only=True)
    signature_image_id = serializers.IntegerField(write_only=True,required=False)
    mail_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = MailRecipient
        fields = [
            "id",
            "recipient_type",
            "user",
            "user_id",
            "signature_image",
            "signature_status",
            "signature_image_id",
            "mail_id",


        ]
    def create(self, validated_data):
        new_mail_recipient= MailRecipient.objects.create(
            **validated_data
        )

        return new_mail_recipient


class MailSerializer(ModelSerializer):
    recipients =MailRecipientSerializer(read_only=True,many=True)
    recipients_list =serializers.ListField(write_only=True,required=True)
    workspace_id = serializers.IntegerField()
    members = MemberSerializer(read_only=True,many=True)
    self_signature_id = serializers.IntegerField(write_only=True,required=False)
    file_id_list = serializers.ListField(write_only=True)
    files = FileDetail(read_only=True,many=True)
    creator_id = serializers.IntegerField(write_only=True)
    creator= MemberSerializer(read_only= True)
    mail_image=FileDetail(read_only=True)
    mail_image_id=serializers.IntegerField(write_only=True,required=False)
    label = MaliLabelSerializer(read_only=True)
    label_id = serializers.IntegerField(write_only=True)

    status_mail=MailStatusSerializer(read_only=True)
    class Meta:
        model = Mail
        fields = [
            "id",
            "creator_id",

            "creator",
            "status_mail",
            "workspace_id",
            "mail_image",
            "mail_image_id",
            "title",
            "label",
            "members",

            "mail_text",
            "slug",
            "files",
            "label_id",
            "self_signature_id",
            "file_id_list",
            "jtime",
            "sign_completed",
            "mail_code",
            "sender_fullname",
            "mail_type",
            "recipients",
            "recipients_list",

           
        ]
    def create(self, validated_data):
        recipients_list =validated_data.pop("recipients_list",[])
        workspace_id = validated_data.pop("workspace_id")

        self_signature_id =validated_data.pop("self_signature_id",None)
        file_id_list= validated_data.pop("file_id_list",[])
        label_id = validated_data.pop("label_id",None)
        mail_image_id= validated_data.pop("mail_image_id",None)
    
     
        new_mail= Mail.objects.create(**validated_data)
        new_mail.workspace = get_object_or_404(WorkSpace,id=workspace_id)
        new_mail.save()
        if mail_image_id:
            new_mail.mail_image_id=mail_image_id
            main_file = MainFile.objects.get(id=mail_image_id)
            main_file.its_blong=True
            main_file.save()
        if label_id:
            label_obj = get_object_or_404(MailLabel,id=label_id)
            new_mail.label=label_obj

        for receiver in recipients_list:
            receiver['mail_id']=new_mail.id
            serializer_data = MailRecipientSerializer(data=receiver)
            if serializer_data.is_valid():
                serializer_data.save()
            else:
                raise serializers.ValidationError(
                    {
                        "status":False,
                        "message":"Validation Error",
                        "data":serializer_data.errors
                    }

                )

        if self_signature_id:
            new_main_file = MainFile.objects.get(id=self_signature_id)
            new_main_file.its_blong = True
            new_main_file.save()
            new_receipt = MailRecipient(
                recipient_type = "sign",
                user_id = validated_data.get("creator_id"),
                signature_image=new_main_file
            )
            new_receipt.save()

        for file_id in file_id_list:
            main_file = MainFile.objects.get(id=file_id)
            
            main_file.its_blong=True
            new_mail.files.add()
            main_file.save()
        new_mail.files.set(file_id_list)
        
        new_mail.save()
        for member in new_mail.members.all():
            new_mail.create_mail_action(user_sender=member,user=new_mail.creator,title="ارسال شد")
            new_mail.create_mail_action(user_sender=new_mail.creator,user=member,title="دریافت شد")

        



        return new_mail
    
class MailActionSerializer(serializers.ModelSerializer):
    user_sender = MemberSerializer(read_only=True)
    owner = MemberSerializer(read_only=True)
    
    class Meta:
        fields =[
            "id",
            "user_sender",
            "title",
            "owner",
        ]



class CategoryDraftSerializer(ModelSerializer):
    workspace_id = serializers.IntegerField(write_only=True)
    owner_id = serializers.IntegerField(write_only=True,required= False)
    class Meta:
        model= CategoryDraft
        fields = [
            "id",
            "title",
            "color_code",
            "workspace_id",
            "owner_id",
        ]
    def create(self, validated_data):
        new_category_draft =CategoryDraft.objects.create(**validated_data)
        return new_category_draft
    def update(self, instance, validated_data):
        validated_data.pop("workspace_id")
        instance.title = validated_data.get("title")
        instance.color_code = validated_data.get("title")
        instance.save()
        return instance
class DraftSerializer(ModelSerializer):
    category= CategoryDraftSerializer(read_only=True)
    members = MemberSerializer(read_only=True,many=True)
    label = MaliLabelSerializer(read_only=True)
    image = FileDetail(read_only=True)
    files= FileDetail(read_only=True,many=True)
    workspace_id = serializers.IntegerField(write_only=True,required=False)
    owner_id= serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True,required=False)
    member_id_list = serializers.ListField(write_only=True,required=False)
    label_id= serializers.IntegerField(write_only=True,required=False)
    image_id = serializers.IntegerField(write_only=True,required=False)
    file_id_list = serializers.ListField(write_only=True,required=False)
    class Meta:
        model = Draft
        fields = [
            "id",
            "draft_name",
            "workspace_id",
            "category_id",
            "member_id_list",
            "label_id",
            "image_id",
            "file_id_list",
            "category",
            "title",
            "image",
            "label",
            "members",
            "signature_status",
            "text",
            "files", 
            "owner_id"
        ]

    def create(self, validated_data):
        member_id_list = validated_data.pop("member_id_list",[])
        file_id_list = validated_data.pop("file_id_list",[])
        image_id = validated_data.pop("image_id",None)
        new_draft_obj = Draft.objects.create(**validated_data)
        if image_id:
            main_file= MainFile.objects.get(id=image_id)
            main_file.its_blong=True
            main_file.save()
            new_draft_obj.image_id=image_id

        new_draft_obj.members.set(member_id_list)

        new_draft_obj.files.set(file_id_list)
        
        new_draft_obj.save()
        for file_id in file_id_list:
            main_file= MainFile.objects.get(id=file_id)
            main_file.its_blong=True
            main_file.save()
        
        return new_draft_obj
        
    def update(self, instance, validated_data):
        
        member_id_list = validated_data.pop("member_id_list",[])
        file_id_list = validated_data.pop("file_id_list",[])
        image_id = validated_data.pop("image_id",None)
        if image_id:
            if image_id != instance.image.id:
                instance.image.delete()
                main_file= MainFile.objects.get(id=image_id)
                main_file.its_blong=True
                instance.image=main_file
            
        instance.members.set(member_id_list)

        instance.draft_name = validated_data.get("draft_name")
        instance.category_id = validated_data.get("category_id")
        instance.label_id = validated_data.get("label_id")
        instance.title = validated_data.get("title")
        instance.signature_status = validated_data.get("signature_status")
        instance.text = validated_data.get("text")
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
        instance.save()