# consumers.py
import json
from django.db.models import Prefetch
from channels.generic.websocket import AsyncWebsocketConsumer,AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from ProjectManager.models import Project,Task,CheckList,CategoryProject
from WorkSpaceManager.models import  WorkSpace,WorkspaceMember,WorkSpacePermission
from asgiref.sync import sync_to_async
from ProjectManager.serializers import TaskSerializer,CheckListSerializer
from UserManager.models import UserAccount



class UploadProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve upload_id from the URL route.
        self.upload_id = self.scope['url_route']['kwargs']['upload_id']
        print(self.upload_id)
        await self.channel_layer.group_add(self.upload_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.upload_id, self.channel_name)

    async def upload_progress(self, event):
        # Send the progress update to the WebSocket client.
        progress = event['progress']
        await self.send(text_data=json.dumps({
            "data_type":"progress_status",
            "progress_percentage":progress
        }))



class CoreWebSocket(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            print("no")
            await self.close(code=4001)
            return

        await self.accept()

        self.user_group_name = f"{self.user.id}_gp_user"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        self.workspace_obj = await self._get_workspace_obj()
    @sync_to_async
    def _get_workspace_obj(self):
        user_account = UserAccount.objects.get(id=self.user.id)
        workspace_obj = WorkSpace.objects.get(id=user_account.current_workspace_id)
        return workspace_obj
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        command = content.get("command")
        data = content.get("data")
        command_handlers = {
            'task_list': self.handle_task_list,
            # 'move_a_task': self.handle_move_task,
            # 'change_sub_task_status': self.handle_subtask_status,
            # 'change_task_status': self.handle_task_status,
            # "read_all_messages": self.read_all_messages,
            # "create_a_message": self.create_a_message,
            # "edit_message": self.edit_message,
        }
        handler = command_handlers.get(command)

        if handler:
            await handler(data)
        else:
            await self.send_error("Invalid command")

    async def send_error(self, message):
        """Helper method for sending error messages"""
        await self.send_json({
            "data_type": "error",
            "message": message,
            "data": {}
        })

    # Project Task Begin
    async def handle_task_list(self, data):
        project_id = data.get("project_id")
        self.project_group_name = f"{project_id}_gp_project"

        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )
        """Handle task list refresh requests"""
        data = await self._main_serializer_data(project_id = project_id)
        await self.send_json({
            "data_type": "task_list",
            "data": data
        })

    @sync_to_async
    def _get_permission_type(self):
        """Get user's permission type for the workspace"""
        try:
            member = WorkspaceMember.objects.get(
                user_account=self.user,
                workspace=self.workspace_obj
            )
            for permission in member.permissions.all():
                if permission.permission_name == "project board":
                    return  permission.permission_type

        except ObjectDoesNotExist:
            return None
    @sync_to_async
    def _has_admin_access(self):

        """Check if user has admin-level permissions"""
        return (
                self.workspace_obj.owner == self.user or
                self._get_permission_type() == "manager"
        )


    def _get_filtered_tasks(self,project_id):
        """Optimized task fetching with smart prefetching."""
        base_qs = Task.objects.filter(
            project_id=project_id,
            done_status=False
        ).select_related('category_task').prefetch_related(
            Prefetch('check_list',
                     queryset=CheckList.objects.select_related('responsible_for_doing'))
        )

        if self._has_admin_access():
            return base_qs
        task_list = []
        for task in base_qs:
            for check_list in task.check_list.all():
                if check_list.responsible_for_doing == self.user:
                    task_list.append(task)
                    break
        return task_list

    @sync_to_async
    def _main_serializer_data(self,project_id):
        """Generate structured task data with categories more efficiently."""
        # Fetch all categories in a single query
        category_objs = CategoryProject.objects.filter(project_id=project_id).order_by("-id")
        all_categories = {cat.id: cat for cat in category_objs}

        # Get tasks with optimized related data fetching
        task_objs = self._get_filtered_tasks(project_id=project_id)

        # Serialize tasks, leveraging pre-fetched related data
        serializer_data = TaskSerializer(task_objs, many=True).data
        print(serializer_data)

        # Organize tasks by category using serializer data
        categories = {}
        for task in serializer_data:
            category_id = task['category_task_id']
            if category_id not in all_categories:
                continue  # Skip invalid categories (data integrity issue)

            # Use category data from serializer to maintain compatibility
            category_data = task["category_task"]
            if category_id not in categories:
                categories[category_id] = {
                    "category_id": category_id,
                    "project_id": project_id,
                    "color": category_data['color_code'],
                    "title": category_data['title'],
                    "task_list": []
                }
            categories[category_id]['task_list'].append(task)

        # Fill in empty categories from pre-fetched data
        for category in category_objs:
            if category.id not in categories:
                categories[category.id] = {
                    "category_id": category.id,
                    "color": category.color_code,
                    "project_id": project_id,
                    "title": category.title,
                    "task_list": []
                }

        # Return sorted results
        return sorted(categories.values(), key=lambda x: x['category_id'])