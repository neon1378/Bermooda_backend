from rest_framework.serializers import Serializer,ModelSerializer
from .models import *
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from core.models import MainFile
from core.serializers import  MainFileSerializer
from MailManager.serializers import MemberSerializer
from UserManager.serializers import MemberSerializer as UserSerializer






class ProjectDepartmentSerializer(ModelSerializer):
    workspace_id = serializers.IntegerField(write_only=True,required=True)
    manager_id = serializers.IntegerField(write_only=True,required=True)
    manager = MemberSerializer(read_only=True)
    class Meta:
        model= ProjectDepartment
        fields=[
            "id",
            "manager",
            "title",
            "workspace_id",
            "manager_id",
        ]

    




class CategoryProjectSerializer(ModelSerializer):
    class Meta:
        model = CategoryProject
        fields= [
            "id",
            "title",
            "order",
            "color_code",

         
        ]



class LabelSerializer(ModelSerializer):
    class Meta:
        model =TaskLabel
        fields = "__all__"

class CheckListSerializer(ModelSerializer):
    label = LabelSerializer()
    file = MainFileSerializer(read_only=True,many=True)
    responsible_for_doing = MemberSerializer(read_only=True)
    label = LabelSerializer(read_only=True)
    class Meta:
        model = CheckList
        fields = [
            "file",
            "label",
            "is_delayed",
            "id",
            "task_data",
            "difficulty",
            "end_date_time_sort",
            "title",
            "status",
            "responsible_for_doing",
            "date_to_start",
            "time_to_start",
            "project_id_main",
            "date_to_end",
            "time_to_end",
        ]
class TaskSerializer(ModelSerializer):
    check_list = CheckListSerializer(many=True)
    category_task = CategoryProjectSerializer()

    class Meta:
        model = Task
        fields = [
            "id",
            "done_status",
            "is_deleted",
            "project_id_main",
            "check_list",
            "title",
            "order",
            "description",
            "category_task",
            "category_task_id",
        ]

    def create(self, validated_data):
        check_list_data = validated_data.pop('check_list')
        task_label = validated_data.pop('task_label')
        validated_data.pop("workspace_id")
        file_id_list = validated_data.pop("file_id_list",[])
           
        category_task_id = validated_data.pop('category_task')['id']

        category_task_obj = get_object_or_404(CategoryProject,id=category_task_id)

   
        task_label_title = task_label['title']
        task_label_color_code = task_label['color_code']
        # if TaskLabel.objects.filter(title= task_label_title).exists():
        #     try:
        #         task_label_obj = TaskLabel.objects.get(title=task_label_title)
        #     except:
        #         task_label_obj = TaskLabel.objects.filter(title= task_label_title)[0]
  
        # else:
        #     task_label_obj = TaskLabel(title=task_label_title,color_code=task_label_color_code)
        #     task_label_obj.save()


        task_obj = Task.objects.create(**validated_data,category_task=category_task_obj)
        
        for file_id in file_id_list :
            try:
                main_file_obj = MainFile.objects.get(id=file_id)
                main_file_obj.its_blong =True
                main_file_obj.save()
                task_obj.main_file.add(main_file_obj)
            except:
                pass 
   
        try:
            last_task = category_task_obj.task_category.last()
            
            task_obj.order= int(last_task.order) +1
        except:
            task_obj.order=1
        task_obj.save()


        for check_list in check_list_data:
            responsible_for_doing_id = check_list['responsible_for_doing']
            user=UserAccount.objects.get(id=responsible_for_doing_id) 
            check_list = CheckList.objects.create( 
                title =check_list['title'],
                status =check_list['status'],
                date_to_start =check_list['date_to_start'],
                time_to_start =check_list['time_to_start'],
                date_to_end =check_list['date_to_end'],
                time_to_end =check_list['time_to_end'],
                responsible_for_doing=user)
            task_obj.check_list.add(check_list)
        return task_obj
    
    def update(self, validated_data):

        check_list_data = validated_data.pop('check_list')
        task_label = validated_data.pop('task_label')
        validated_data.pop("workspace_id")
        file_id_list = validated_data.pop("file_id_list",[])

        

    














class TaskReportSerializer(serializers.ModelSerializer):
    creator = MemberSerializer(read_only=True)
    class Meta:
        model = TaskReport
        fields = [
            "id",
            "file",
            "body",
            "replay",
            "creator",
            "jtime",
            "replay_text",
            "creator_detail",
            "file_urls",
            "created",
            # "parent_id"
            
        ]


    def create(self, validated_data):
        # validated_data.get("replay")
        
        print(validated_data)


class ProjectChatSerializer(ModelSerializer):
    main_file_id= serializers.IntegerField(write_only=True,required=False)
    voice_file_id = serializers.IntegerField(write_only=True,required=False)
    project_id = serializers.IntegerField(write_only=True,required=True)
    creator_id = serializers.IntegerField(write_only=True,required=True)
    creator = MemberSerializer(read_only=True)
    class Meta:
        model = ProjectChat
        fields = [
                "main_file_id",
                "voice_file_id",
                "body",
                "creator_id",
                "file_url",
                "voice_url",
                "creator",
                "jcreated",
                "project_id",
                "creator_detail",
        ]
    def create(self, validated_data):
        main_file_id = validated_data.pop("main_file_id",None)
        voice_file_id = validated_data.pop("voice_file_id",None)
    
        project_chat_obj = ProjectChat.objects.create(**validated_data)
        project_chat_obj.save()
        return project_chat_obj



class ProjectSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    category_project = CategoryProjectSerializer(many=True, read_only=True)
    department = ProjectDepartmentSerializer(read_only=True)
    avatar_id = serializers.IntegerField(write_only=True, required=False)
    department_id = serializers.IntegerField(write_only=True, required=True)
    workspace_id = serializers.IntegerField(write_only=True, required=True)
    users = serializers.ListField(write_only=True, required=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "avatar_url",
            "category_project",
            "members",
            "project_status",
            "avatar_id",
            "department_id",
            "department",
            "workspace_id",
            "users",
        ]

    def create(self, validated_data):
        user = self.context.get("user")
        users = validated_data.pop("users", [])
        avatar_id = validated_data.pop("avatar_id", None)
        project_obj = Project.objects.create(**validated_data)
        if user.id not in users:
            users.append(user.id)

        for user in users:
            user_acc = UserAccount.objects.get(id=user)
            project_obj.members.add(user_acc)
        if avatar_id:
            main_file = MainFile.objects.get(id=avatar_id)
            main_file.its_blong = True
            main_file.save()
            project_obj.avatar = main_file
        categories = [
            {"title": "برای انجام", "order": 1, "color_code": "#DB4646"},
            {"title": "در حال انجام", "order": 2, "color_code": "#02C875"},
            {"title": "انجام شده", "order": 3, "color_code": "#9C00E8"},
            {"title": "تست", "order": 4, "color_code": "#E82BA3"},
        ]
        category_objs = [
            CategoryProject(
                title=category['title'],
                color_code=category['color_code'],
                order=category['order'],
                project=project_obj
            ) for category in categories
        ]
        CategoryProject.objects.bulk_create(category_objs)
        project_obj.save()
        return project_obj

    def update(self, instance, validated_data):
        users = validated_data.pop("users", None)
        avatar_id = validated_data.pop("avatar_id", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if users is not None:
            instance.members.clear()
            for user in users:
                user_acc = UserAccount.objects.get(id=user)
                instance.members.add(user_acc)

        if avatar_id and avatar_id != getattr(instance.avatar, 'id', None):
            if instance.avatar:
                instance.avatar.delete()
            instance.avatar_id = avatar_id
            main_file_obj = MainFile.objects.get(id=avatar_id)
            main_file_obj.its_blong=True
            main_file_obj.save()

        instance.save()
        return instance








class ProjectMessageSerializer(ModelSerializer):
    file = MainFileSerializer(read_only=True,many=True)
    file_id_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    replay = serializers.SerializerMethodField(read_only=True)
    replay_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    creator = UserSerializer(read_only=True)
    creator_id = serializers.IntegerField(write_only=True,required=True)
    project = ProjectSerializer(read_only=True)
    related_instance = serializers.SerializerMethodField(read_only=True)
    project_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model = ProjectMessage
        fields = [
            "id",
            "body",
            "project",
            "project_id",
            "related_instance",
            "message_type",
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
        user = self.context.get('user')

        data['self'] = user == instance.creator
        return data
    def get_related_instance(self,obj):
        if obj.related_object:
            object_name = obj.related_object.__class__.__name__
            if object_name == "Task":
                data = {
                    "data_type":"task_data",
                    "data":TaskSerializer(obj.related_object).data,

                }
                return data
            elif object_name == "CheckList":
                data ={
                    "data_type":"check_list_data",
                    "data":CheckListSerializer(CheckList).data
                }
                return data
    def get_replay(self, obj):
        if obj.replay:
            return ProjectMessageSerializer(obj.replay).data
        return None
    def create(self, validated_data):
        file_id_list = validated_data.pop("file_id_list",None)
        replay_id = validated_data.pop("replay_id",None)
        new_message = ProjectMessage.objects.create(**validated_data)
        if replay_id:
            new_message.replay_id = replay_id
        if file_id_list:
            main_files = MainFile.objects.filter(id__in=file_id_list)
            for main_file in main_files:
                main_file.its_belong = True
                main_file.save()
                new_message.file.add(main_file)
        new_message.message_type="text"
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


