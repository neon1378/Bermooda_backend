from rest_framework import serializers
from .models import *
from core.serializers import MainFileSerializer,CitySerializer,StateSerializer,CountrySerializer
from UserManager.serializers import MemberSerializer
from core.widgets import persian_to_gregorian
from core.models import MainFile
from django.shortcuts import get_object_or_404
from UserManager.serializers import MemberSerializer
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
        category_list = [
            {
                "title":"تایید شده",
                "color_code":"#35dba8"
            },
            {
                "title":"تایید نشده",
                "color_code":"#747a80"
            }

        ]
        for item in category_list:
            new_category = FolderCategory.objects.create(
                title=item["title"],
                color_code=item["color_code"],
                folder = new_folder
            )

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



class FolderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderCategory
        fields = [
            "slug",
            "title",
            "color_code",


        ]



class EmployeeRequestSerializer(serializers.ModelSerializer):
    # Write-only IDs and slugs
    state_id = serializers.IntegerField(write_only=True, required=False)
    city_id = serializers.IntegerField(write_only=True, required=False)
    requesting_user_id = serializers.IntegerField(write_only=True, required=True)
    leave_file_id_list = serializers.ListField(write_only=True, required=False)
    doctor_document_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    folder_category_slug = serializers.SlugField(write_only=True, required=False)
    country_id = serializers.IntegerField(write_only=True, required=False)
    country = CountrySerializer(read_only=True)
    # Read-only nested
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    requesting_user = MemberSerializer(read_only=True)
    leave_file_documents = MainFileSerializer(many=True, read_only=True)
    doctor_document = MainFileSerializer(read_only=True)
    folder_category = FolderCategorySerializer(read_only=True)

    # Date/time fields
    date_time_to_start = serializers.CharField(read_only=True,required=False)
    date_time_to_end = serializers.CharField(read_only=True, required=False)
    start_date = serializers.CharField(write_only=True,required=False)
    end_date = serializers.CharField(write_only=True, required=False)
    hourly_leave_date_at = serializers.CharField(write_only=True, required=False)
    time_to_start = serializers.CharField(write_only=True, required=False)
    time_to_end = serializers.CharField(write_only=True, required=False)


    class Meta:
        model = EmployeeRequest
        fields = [
            'id', 'mission_type',
            'state', 'state_id', 'city', 'city_id',
            'address', 'description', 'vehicle',
            'date_time_to_start', 'date_time_to_end',
            'requesting_user', 'requesting_user_id',
            'leave_type', 'request_type', 'reason_for_leave',
            'leave_file_documents', 'leave_file_id_list',
            'start_date', 'end_date', 'start_date_at', 'end_date_at',
            'hourly_leave_date_at', 'hourly_leave_date',
            'time_to_start', 'time_to_end', 'time_to_start_at', 'time_to_end_at',
            'doctor_document', 'doctor_document_id', 'doctor_name',
            'name_of_treatment_center',
            'emergency_type',
            'folder_category', 'folder_category_slug',
             'slug',
            "country_id","country",

            "date_time_to_start_jalali","date_time_to_end_jalali",
            "start_date_jalali","end_date_jalali","hourly_leave_date_jalali",

            "resource_title","model","resource_count","reason_for_resources",
            "status",
        ]

    def validate(self, attrs):
        """Validate fields based on request_type and leave_type."""
        request_type = attrs.get('request_type')
        mission_type = attrs.get('mission_type')
        if not request_type:
            raise serializers.ValidationError({'request_type': 'This field is required.'})

        if request_type == 'leave':
            leave_type = attrs.get('leave_type')
            if not leave_type:
                raise serializers.ValidationError({'leave_type': 'This field is required for leave requests.'})

            if leave_type == 'daily_leave':
                if not attrs.get('start_date') or not attrs.get('end_date'):
                    raise serializers.ValidationError({'start_date': 'start_date and end_date are required for daily_leave.'})

            elif leave_type == 'hourly_leave':
                missing = [f for f in ('hourly_leave_date_at','time_to_start','time_to_end') if not attrs.get(f)]
                if missing:
                    raise serializers.ValidationError({f: 'Required for hourly_leave.' for f in missing})

            elif leave_type == 'sick_leave':
                missing = [f for f in ('start_date','end_date','doctor_document_id') if not attrs.get(f)]
                if missing:
                    raise serializers.ValidationError({f: 'Required for sick_leave.' for f in missing})

            elif leave_type == 'unpaid_leave':
                if not attrs.get('start_date') or not attrs.get('end_date'):
                    raise serializers.ValidationError({'start_date and end_date are required for unpaid_leave.'})

            elif leave_type == 'incentive_leave':

                if not attrs.get('start_date_at') or attrs.get('end_date_at'):
                    raise serializers.ValidationError({'start_date_at and end_date_at Required for incentive_leave.'})

            elif leave_type == 'emergency_leave':
                emergency_type = attrs.get('emergency_type')
                if not emergency_type:
                    raise serializers.ValidationError({'emergency_type': 'Required for emergency_leave.'})
                if emergency_type == 'daily':
                    if not attrs.get('start_date') or not attrs.get('end_date'):
                        raise serializers.ValidationError({'start_date': 'start_date and end_date required for daily emergency_leave.'})
                elif emergency_type == 'hourly':
                    missing = [f for f in ('time_to_start','time_to_end') if not attrs.get(f)]
                    if missing:
                        raise serializers.ValidationError({f: 'Required for hourly emergency_leave.' for f in missing})
                else:
                    raise serializers.ValidationError({'emergency_type': 'Invalid emergency_type.'})

            else:
                raise serializers.ValidationError({'leave_type': 'Invalid leave_type.'})

        elif request_type == 'administrative_mission':
            if not mission_type:
                raise serializers.ValidationError({'mission_type': 'This field is required.'})
            if mission_type == "inside":

                missing = [f for f in ('city_id','state_id','mission_type','date_time_to_start','date_time_to_end') if not attrs.get(f)]
                if missing:
                    raise serializers.ValidationError({f: 'Required for administrative_mission.' for f in missing})
            else:

                missing = [f for f in ( "country_id",'mission_type', 'date_time_to_start', 'date_time_to_end')
                           if not attrs.get(f)]
                if missing:

                    raise serializers.ValidationError({f: 'Required for administrative_mission.' for f in missing })

        elif request_type == 'resources':
            missing = [att for att in ("resource_title" ,"model","resource_count") if not attrs.get(att)]
            if missing:
                raise serializers.ValidationError({f: 'Required for resources.' for f in missing})

        return attrs

    def create(self, validated_data):
        # Same as before; fields already validated
        # Pop write-only
        state_id = validated_data.pop('state_id', None)
        city_id = validated_data.pop('city_id', None)
        requesting_user_id = validated_data.pop('requesting_user_id')
        leave_file_ids = validated_data.pop('leave_file_id_list', [])
        doctor_document_id = validated_data.pop('doctor_document_id', None)
        user = self.context.get("user")
        workspace_obj = self.context.get("workspace_obj")
        folder_category_slug = validated_data.pop('folder_category_slug', None)

        # Date/time pops
        start_date = validated_data.pop('start_date', None)
        end_date = validated_data.pop('end_date', None)
        hourly_date = validated_data.pop('hourly_leave_date_at', None)
        t_start = validated_data.pop('time_to_start', None)
        t_end = validated_data.pop('time_to_end', None)

        m_type = validated_data.pop('mission_type', None)
        dt_start = validated_data.pop('date_time_to_start', None)
        dt_end = validated_data.pop('date_time_to_end', None)
        country_id = validated_data.pop('country_id', None)
        resource_title = validated_data.pop("resource_title",None)
        model = validated_data.pop("model",None)
        resource_count = validated_data.pop("resource_count",None)
        reason_for_resources =validated_data.pop("reason_for_resources",None)
        req = EmployeeRequest(requesting_user_id=requesting_user_id)

        req.request_type = validated_data.get('request_type')

        # Handle leave and administrative mission as validated
        if req.request_type == 'leave':
            req.leave_type = validated_data.get('leave_type')
            # Assign dates/times
            if req.leave_type == 'daily_leave':
                req.start_date_at = persian_to_gregorian(start_date).date() if persian_to_gregorian(start_date) else None
                req.end_date_at = persian_to_gregorian(end_date).date() if persian_to_gregorian(end_date) else None
            elif req.leave_type == 'hourly_leave':
                req.hourly_leave_date = persian_to_gregorian(hourly_date).date() if persian_to_gregorian(hourly_date) else None
                req.time_to_start_at = t_start
                req.time_to_end_at = t_end
            elif req.leave_type == 'sick_leave':
                req.start_date_at = persian_to_gregorian(start_date).date()  if persian_to_gregorian(start_date) else None
                req.end_date_at = persian_to_gregorian(end_date).date() if persian_to_gregorian(end_date) else None
                req.doctor_document_id = doctor_document_id
                req.doctor_name = validated_data.get('doctor_name')
                req.name_of_treatment_center = validated_data.get('name_of_treatment_center')
            elif req.leave_type == 'unpaid_leave':
                req.start_date_at = persian_to_gregorian(start_date).date() if persian_to_gregorian(start_date) else None
                req.end_date_at = persian_to_gregorian(end_date).date() if persian_to_gregorian(end_date) else None
            elif req.leave_type == 'incentive_leave':
                req.start_date_at = persian_to_gregorian(end_date).date() if persian_to_gregorian(end_date) else None
                req.start_date_at = persian_to_gregorian(start_date).date() if persian_to_gregorian(start_date) else None
            elif req.leave_type == 'emergency_leave':
                req.emergency_type = validated_data.get('emergency_type')
                if req.emergency_type == 'daily':
                    req.start_date_at = persian_to_gregorian(start_date).date() if persian_to_gregorian(start_date) else None
                    req.end_date_at = persian_to_gregorian(end_date).date() if persian_to_gregorian(end_date) else None
                else:
                    req.time_to_start_at = t_start
                    req.time_to_end_at = t_end

            if validated_data.get('reason_for_leave'):
                req.reason_for_leave = validated_data.get('reason_for_leave')

            for fid in leave_file_ids:
                mf = MainFile.objects.get(id=fid)
                mf.its_blong = True
                req.leave_file_documents.add(mf)


        elif req.request_type == "resources":
            req.resource_title = resource_title
            req.model = model
            req.resource_count = resource_count
            if reason_for_resources:
                req.reason_for_resources=reason_for_resources
        else:  # administrative_mission
            if city_id:
                req.city_id = city_id
            if state_id:
                req.state_id = state_id
            req.mission_type = m_type
            if country_id:
                req.country_id=country_id
            req.date_time_to_start_at = persian_to_gregorian(dt_start)
            req.date_time_to_end_at = persian_to_gregorian(dt_end)
            req.address = validated_data.get('address')
            req.description = validated_data.get('description')
            req.vehicle = validated_data.get('vehicle')

        # Folder
        if folder_category_slug:
            req.folder_category = get_object_or_404(FolderCategory, slug=folder_category_slug)
        workspace_member = WorkspaceMember.objects.filter(user_account=user,workspace=workspace_obj).first()
        req.folder = workspace_member.folder



        req.save()
        return req

    def update(self, instance, validated_data):
        # Re-validate via validate()
        self.validate(validated_data)
        # Pop write-only
        state_id = validated_data.pop('state_id', None)
        city_id = validated_data.pop('city_id', None)
        leave_file_ids = validated_data.pop('leave_file_id_list', None)
        doctor_document_id = validated_data.pop('doctor_document_id', None)

        country_id= validated_data.pop('country_id', None)
        folder_category_slug = validated_data.pop('folder_category_slug', None)
        user = self.context.get("user")
        workspace_obj = self.context.get("workspace_obj")
        # Date/time pops
        start_date = validated_data.pop('start_date', None)
        end_date = validated_data.pop('end_date', None)
        hourly_date = validated_data.pop('hourly_leave_date_at', None)
        t_start = validated_data.pop('time_to_start', None)
        t_end = validated_data.pop('time_to_end', None)

        m_type = validated_data.pop('mission_type', None)
        dt_start = validated_data.pop('date_time_to_start', None)
        dt_end = validated_data.pop('date_time_to_end', None)

        # Simple fields
        for attr, val in validated_data.items(): setattr(instance, attr, val)
        if state_id is not None: instance.state_id = state_id
        if city_id is not None: instance.city_id = city_id
        if doctor_document_id is not None: instance.doctor_document_id = doctor_document_id

        # Dates/times


        if start_date: instance.start_date_at = persian_to_gregorian(start_date)
        if country_id: instance.country_id = country_id

        if end_date: instance.end_date_at = persian_to_gregorian(end_date)
        if hourly_date: instance.hourly_leave_date = persian_to_gregorian(hourly_date)
        if t_start: instance.time_to_start_at = t_start
        if t_end: instance.time_to_end_at = t_end

        if dt_start: instance.date_time_to_start_at = persian_to_gregorian(dt_start)
        if dt_end: instance.date_time_to_end_at = persian_to_gregorian(dt_end)
        if m_type: instance.mission_type = m_type

        # Files
        if leave_file_ids is not None:
            instance.leave_file_documents.clear()
            for fid in leave_file_ids:
                mf = MainFile.objects.get(id=fid); mf.its_blong = True; instance.leave_file_documents.add(mf)

        if folder_category_slug:
            instance.folder_category = get_object_or_404(FolderCategory, slug=folder_category_slug)
        workspace_member = WorkspaceMember.objects.filter(user_account=user,workspace=workspace_obj).first()
        instance.folder = workspace_member.folder

        instance.save()
        # Folder
        return instance


