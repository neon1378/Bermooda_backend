from rest_framework.serializers import Serializer,ModelSerializer
from .models import *
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from core.models import MainFile
from MailManager.serializers import MemberSerializer

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
            "title"

         
        ]



class LabelSerializer(ModelSerializer):
    class Meta:
        model =TaskLabel
        fields = "__all__"
class CheckListSerializer(ModelSerializer):
    label = LabelSerializer()
    responsible_for_doing = MemberSerializer(read_only=True)
    label = LabelSerializer(read_only=True)
    class Meta:
        model = CheckList
        fields = [
            "label",
            "id",
            "title",
            "status",
            "responsible_for_doing",
            "date_to_start",
            "time_to_start",
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