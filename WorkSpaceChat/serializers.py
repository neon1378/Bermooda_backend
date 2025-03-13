from UserManager.serializers import UserAccountSerializer
from .models import  *
from rest_framework import serializers
from UserManager.models import UserAccount
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model= UserAccount
        fields = [
            "id",
            "fullname",
            "avatar_url",
            "is_online",

        ]


class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True,read_only=True)
    workspace_id = serializers.IntegerField(write_only=True,required=True)
    member_id_list = serializers.ListField(write_only=True,required=True)
    class Meta:
        model = GroupMessage
        fields = [
            "id",
            "members",
            "workspace_id",
            "member_id_list",

            # "workspace",
        ]
    def create(self, validated_data):
        member_id_list =validated_data.pop("member_id_list",[])
        group_message = GroupMessage.objects.create(**validated_data)
        for member_id in member_id_list:
            group_message.members.add(
                UserAccount.objects.get(id=member_id)
            )
        group_message.save()
        return group_message



class TextMessageSerializer(serializers.ModelSerializer):
    owner = UserAccountSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True,required=True)
    group_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model = TextMessage
        fields = [
            "id",
            "text",
            "owner",
            "owner_id",
            "created_at",
            "group_id",
            "jalali_time",
            "jalali_date",

        ]
    def create(self, validated_data):
        new_text_message = TextMessage.objects.create(**validated_data)
        return  new_text_message


