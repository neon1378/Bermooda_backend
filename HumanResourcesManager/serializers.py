from rest_framework import serializers
from .models import *
from core.serializers import MainFileSerializer
from UserManager.serializers import MemberSerializer
from core.models import MainFile
from django.shortcuts import get_object_or_404
from WorkSpaceManager.models import WorkSpace,WorkspaceMember

class FolderSerializer(serializers.ModelSerializer):
    workspace_id = serializers.IntegerField(required=True)
    avatar = MainFileSerializer(read_only=True)
    avatar_id = serializers.IntegerField(required=False, allow_null=True)

    member_id_list = serializers.ListField(write_only=True, required=True)

    class Meta:
        model = Folder
        fields = [
            "id",
            "title",
            "avatar",
            "avatar_id",
            "workspace_id",
            "created_at",
            "slug",

            "member_id_list",
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['members']= MemberSerializer(instance.members.all(),many=True,context={"workspace_id":instance.workspace.id}).data
        return data
    def create(self, validated_data):
        workspace_id = validated_data.get("workspace_id")
        workspace_obj = WorkSpace.objects.get(id=workspace_id)
        avatar_id = validated_data.pop("avatar_id", None)
        member_id_list = validated_data.pop("member_id_list", [])
        new_folder = Folder.objects.create(**validated_data)
        if avatar_id:
            main_file = MainFile.objects.get(id=avatar_id)
            main_file.its_blong = True
            main_file.workspace_id = new_folder.workspace.id
            main_file.save()
            new_folder.avatar = main_file

        for member_id in member_id_list:
            if workspace_obj.owner.id == member_id:
                if not WorkspaceMember.objects.filter(user_account_id=member_id, workspace=workspace_obj).exists():
                    WorkspaceMember.objects.create(
                        user_account_id=member_id,
                        workspace=workspace_obj,
                        fullname=workspace_obj.owner.fullname,
                        is_accepted=True,

                    )
                    user_acc = get_object_or_404(UserAccount, id=member_id)
                    new_folder.members.add(user_acc)
                else:
                    user_acc = get_object_or_404(UserAccount, id=member_id)
                    new_folder.members.add(user_acc)
            else:
                user_acc = get_object_or_404(UserAccount, id=member_id)
                new_folder.members.add(user_acc)

        new_folder.save()
        if not member_id_list or member_id_list == []:
            new_folder.members.add(new_folder.workspace.owner)
        new_folder.save()
        return new_folder

    def update(self, instance, validated_data):
        workspace_id = validated_data.get("workspace_id")
        workspace_obj = WorkSpace.objects.get(id=workspace_id)
        avatar_id = validated_data.pop("avatar_id", None)
        member_id_list = validated_data.pop("member_id_list", None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update avatar if provided
        if avatar_id is not None and avatar_id != instance.avatar.id:
            instance.avatar.delete()
            main_file = MainFile.objects.get(id=avatar_id)
            main_file.its_blong = True
            main_file.workspace_id = instance.workspace.id
            main_file.save()
            instance.avatar = main_file

        # Update members if provided
        if member_id_list is not None:
            instance.members.clear()
            for member_id in member_id_list:
                if workspace_obj.owner.id == member_id:
                    if not WorkspaceMember.objects.filter(user_account_id=member_id,workspace=workspace_obj).exists():
                        WorkspaceMember.objects.create(
                            user_account_id=member_id,
                            workspace=workspace_obj,
                            fullname=workspace_obj.owner.fullname,
                            is_accepted=True,
                        )
                        user_acc = get_object_or_404(UserAccount, id=member_id)
                        instance.members.add(user_acc)
                    else:
                        user_acc = get_object_or_404(UserAccount, id=member_id)
                        instance.members.add(user_acc)
                else:
                    user_acc = get_object_or_404(UserAccount, id=member_id)
                    instance.members.add(user_acc)
        if not member_id_list or member_id_list == []:
            instance.members.add(instance.workspace.owner)
        instance.save()
        return instance


