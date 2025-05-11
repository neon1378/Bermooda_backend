from rest_framework.serializers import Serializer,ModelSerializer
from .models import *
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from core.models import MainFile
from core.serializers import  MainFileSerializer
from MailManager.serializers import MemberSerializer
from UserManager.serializers import MemberSerializer as UserSerializer
from core.widgets import persian_to_gregorian,create_reminder
from Notification.views import  create_notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



def create_reminde_a_task(chek_list):
    if chek_list.date_time_to_start_main:
        title = "یاد آوری وظیفه"
        short_text = ' '.join(chek_list.title.split()[:15]) + ('...' if len(chek_list.title.split()) > 15 else '')
        sub_title = f"وقت شروع وظیفه  {short_text} هست "
        create_reminder(related_instance=chek_list, remind_at=chek_list.date_time_to_start_main, title=title, sub_title=sub_title)
    elif chek_list.date_time_to_end_main:
        title = "یاد آوری وظیفه",
        short_text = ' '.join(chek_list.title.split()[:15]) + ('...' if len(chek_list.title.split()) > 15 else '')
        sub_title = f"تایم انجام وظیفه {short_text} تمام شده است  "
        create_reminder(related_instance=chek_list, remind_at=chek_list.date_time_to_start_main, title=title,
                        sub_title=sub_title)


def create_notify_message(message,related_instance,project_id,creator_id):
    content_type = ContentType.objects.get_for_model(related_instance.__class__)
    message_obj = ProjectMessage.objects.create(
        message_type="notification",
        content_type=content_type,
        object_id=related_instance.id,
        body=message,
        project_id=project_id,
        creator_id=creator_id
    )
    channel_layer = get_channel_layer()
    event = {
                "type": "send_a_message",
                "message_id": message_obj.id

            }

    async_to_sync(channel_layer.group_send)(f"{project_id}_gp_project", event)
    return True
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

class CheckListTimerSerializer(ModelSerializer):
    class Meta:
        model = CheckListTimer
        fields = [
            "id",
            "status",
            "is_done",
            "get_elapsed_seconds",

        ]

class CheckListSerializer(ModelSerializer):

    file = MainFileSerializer(read_only=True,many=True)
    timer = CheckListTimerSerializer(read_only=True)
    label = LabelSerializer(read_only=True)
    label_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    file_id_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    responsible_for_doing_id = serializers.IntegerField(write_only=True,required=False,allow_null=True)
    responsible_for_doing = UserSerializer(read_only=True)
    task_id = serializers.IntegerField(required=True,write_only=True)
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

            "date_to_start",
            "time_to_start",
            "project_id_main",
            "date_to_end",
            "time_to_end",
            #new
            "label_id",
            "file_id_list",
            "responsible_for_doing_id",
            "responsible_for_doing",
            "task_id",
            "check_list_type",
            "timer",
        ]
    def create(self, validated_data):
        user = self.context.get("user")
        date_to_start = validated_data.get("date_to_start",None)
        time_to_start = validated_data.get("time_to_start",None)
        date_to_end = validated_data.get("date_to_end",None)
        time_to_end = validated_data.get("time_to_end", None)
        file_id_list = validated_data.pop("file_id_list",[])
        title = validated_data.get("title")
        responsible_for_doing_id = validated_data.get("responsible_for_doing_id", None)
        task_id = validated_data.pop("task_id")
        label_id = validated_data.pop("label_id",None)
        task_obj = get_object_or_404(Task,id=task_id)
        check_list_type = validated_data.pop("check_list_type",None)

        if date_to_start and time_to_start and date_to_end and time_to_end:
            try:
                date_time_to_start = f"{date_to_start} {time_to_start}"
                date_time_to_end = f"{date_to_end} {time_to_end}"

                date_time_start_obj = jdatetime.datetime.strptime(date_time_to_start, "%Y/%m/%d %H:%M")
                date_time_end_obj = jdatetime.datetime.strptime(date_time_to_end, "%Y/%m/%d %H:%M")
                if date_time_start_obj >= date_time_end_obj:
                    raise serializers.ValidationError(
                        {
                            "status": False,
                            "message": f"در چک لیست {title} تاریخ شروع و پایان درست نمیباشد"
                        }
                    )
            except:
                pass


        check_list_obj = CheckList.objects.create(
            **validated_data,
            task=task_obj,

            date_time_to_start_main=persian_to_gregorian(f"{date_to_start} {time_to_start}"),
            date_time_to_end_main=persian_to_gregorian(f"{date_to_end} {time_to_end}")
        )
        if label_id :
            check_list_obj.label_id=label_id
        if responsible_for_doing_id:
            check_list_obj.responsible_for_doing_id=responsible_for_doing_id
        if file_id_list:
            for file_id in file_id_list:
                main_file = MainFile.objects.get(id=file_id)
                main_file.its_blong = True
                main_file.save()
                check_list_obj.file.add(main_file)
        check_list_obj.save()
        if check_list_type:
            check_list_obj.check_list_type=check_list_type
            if check_list_type == "based_on_weight":
                try:
                    CheckListTimer.objects.create(check_list=check_list_obj)
                except:
                    pass

        return check_list_obj

    def update(self, instance, validated_data):
        user = self.context.get("user")
        label_id = validated_data.get("label_id", None)
        title = validated_data.get("title",None)
        responsible_for_doing_id = validated_data.get("responsible_for_doing_id", None)
        date_to_start = validated_data.get("date_to_start", None)
        time_to_start = validated_data.get("time_to_start", None)
        date_to_end = validated_data.get("date_to_end", None)
        time_to_end = validated_data.get("time_to_end", None)
        difficulty = validated_data.get("difficulty", None)

        if label_id:
            instance.label_id = label_id

        if responsible_for_doing_id:
            instance.responsible_for_doing_id = responsible_for_doing_id

        instance.title = title
        instance.date_to_start = date_to_start
        instance.time_to_start = time_to_start
        instance.date_to_end = date_to_end
        instance.time_to_end = time_to_end
        try:
            instance.date_time_to_start_main = persian_to_gregorian(f"{date_to_start} {time_to_start}")
        except:
            pass

        try:
            instance.date_time_to_end_main = persian_to_gregorian(f"{date_to_end} {time_to_end}")
        except:
            pass

        instance.difficulty = difficulty
        existing_file_ids = list(instance.file.values_list("id", flat=True))

        # Update associated files
        file_ids = validated_data.get("file_id_list", [])
        MainFile.objects.filter(id__in=file_ids).update(its_blong=True)
        instance.file.set(MainFile.objects.filter(id__in=file_ids))

        # Identify and delete files that are no longer associated with the task
        removed_file_ids = set(existing_file_ids) - set(file_ids)
        MainFile.objects.filter(id__in=removed_file_ids).delete()
        instance.save()

        return instance

class TaskSerializer(ModelSerializer):
    check_list = CheckListSerializer(many=True,read_only=True)
    category_task = CategoryProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True,required=True)
    file_id_list = serializers.ListField(write_only=True,required=False,allow_null=True)
    file_urls = serializers.SerializerMethodField(read_only=True)
    check_list_data = serializers.ListField(write_only=True,required=False,allow_null=True)
    category_task_id = serializers.IntegerField(write_only=True,required=True)
    workspace_id = serializers.IntegerField(write_only=True,required=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "done_status",

            "is_deleted",
            "project_id_main",
            "check_list",
            "title",
            "file_urls",
            "order",
            "description",
            "category_task",
            "category_task_id",

            #new
            "task_progress",
            "file_id_list",
            "project_id",
            "check_list_data",
            "workspace_id",


        ]


    def get_file_urls(self,obj):
        return MainFileSerializer(obj.main_file.all(),many=True).data
    def create(self, validated_data):
        try:
            done_status= validated_data.pop("done_status",None)
        except:
            pass
        project_id = validated_data.pop("project_id")
        check_list_data = validated_data.pop("check_list_data", None)
        file_ids = validated_data.pop("file_id_list",None)
        category_id = validated_data.pop("category_task_id")
        workspace_id = validated_data.pop("workspace_id")
        project = get_object_or_404(Project, id=project_id)

        user = self.context.get("user")









        category = get_object_or_404(CategoryProject, id=category_id)

        task = Task.objects.create(
            **validated_data, category_task_id=category_id, project_id=project_id
        )
        task.project=project
        # Associate files with the task
        MainFile.objects.filter(id__in=file_ids).update(its_blong=True)
        task.main_file.add(*MainFile.objects.filter(id__in=file_ids))

        # Set task order
        last_task = category.task_category.order_by("order").last()
        task.order = (last_task.order + 1) if last_task else 1
        task.save()


        # Create checklist items
        checklist_serializers = []
        for check_list_item in check_list_data:

            if not check_list_item['responsible_for_doing_id']:
                check_list_item['responsible_for_doing_id'] = user.id
            task_id = task.id
            check_list_item['task'] = task


            serializer = CheckListSerializer(data=check_list_item)

            serializer.is_valid(raise_exception=True)

            checklist_serializers.append(serializer)
        for serializer in checklist_serializers:
            serializer.save()


        task.save()





        return task
    def update(self, instance, validated_data):
        # Update task fields

        user = self.context.get("user")
        file_ids = validated_data.get("file_id_list",[])
        instance.title = validated_data.get("title")
        workspace_id = validated_data.pop("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        instance.description = validated_data.get("description")

        existing_file_ids = list(instance.main_file.values_list("id", flat=True))

        # Update associated files

        MainFile.objects.filter(id__in=file_ids).update(its_blong=True)
        instance.main_file.set(MainFile.objects.filter(id__in=file_ids))

        # Identify and delete files that are no longer associated with the task
        removed_file_ids = set(existing_file_ids) - set(file_ids)
        MainFile.objects.filter(id__in=removed_file_ids).delete()


        return instance
        

    














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
    related_object = serializers.SerializerMethodField(read_only=True)
    project_id = serializers.IntegerField(write_only=True,required=True)
    class Meta:
        model = ProjectMessage
        fields = [
            "id",
            "body",
            "project",
            "project_id",
            "related_object",
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
    def get_related_object(self,obj):
        if obj.related_object:
            object_name = obj.related_object.__class__.__name__
            if object_name == "Task":
                data = {
                    "data_type":"task_data",
                    "project_id":obj.related_object.project.id,
                    "data":TaskSerializer(obj.related_object).data,

                }
                return data
            elif object_name == "CheckList":
                data ={
                    "data_type":"check_list_data",
                    "project_id":obj.related_object.task.project.id,
                    "data":CheckListSerializer(obj.related_object).data
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


