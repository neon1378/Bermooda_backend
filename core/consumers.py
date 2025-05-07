# consumers.py
import json
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncWebsocketConsumer,AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from ProjectManager.models import Project,Task,CheckList,CategoryProject,ProjectMessage
from WorkSpaceManager.models import  WorkSpace,WorkspaceMember,WorkSpacePermission
from asgiref.sync import sync_to_async
from ProjectManager.serializers import TaskSerializer,CheckListSerializer,ProjectMessageSerializer
from UserManager.models import UserAccount
from .widgets import  pagination

from CrmCore.models import CustomerUser,GroupCrm,Label,CustomerStep
from CrmCore.serializers import CustomerSmallSerializer,GroupCrmSerializer,LabelStepSerializer

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

    async def send_extra(self,data):
        event = {
            "type":"send_event_task_list",
            "project_id":data.get("project_id"),
        }
        await self.channel_layer.group_send(
            self.project_group_name,
            event
        )
    async def receive_json(self, content, **kwargs):
        command = content.get("command")
        data = content.get("data",None)
        print (data)
        command_handlers = {
            'task_list': self.handle_task_list,
            'move_a_task': self.handle_move_task,
            'change_sub_task_status': self.handle_subtask_status,

            'change_task_status': self.handle_task_status,

            "read_all_messages": self.read_all_messages,

            "create_a_message": self.create_a_message_handler,

            "edit_message": self.edit_message_handler,

            # Crm WebSocket Commands
            "customer_list":self.customer_list_handler,
            "change_step_status":self.change_step_status_handler,

            # "send_extra":self.send_extra,
        }
        handler = command_handlers.get(command)

        if handler:
            if command == "task_list" or command == "read_all_messages":
                project_id = data.get("project_id")
                self.project_group_name = f"{project_id}_gp_project"

                await self.channel_layer.group_add(
                    self.project_group_name,
                    self.channel_name
                )
            if command == "customer_list":
                group_crm_id = data.get("group_crm_id")
                self.crm_group_name = f"{group_crm_id}_gp_group_crm"
                await self.channel_layer.group_add(
                    self.crm_group_name,
                    self.channel_name
                )
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

    # Crm Customer Begin
    async def change_step_status_handler(self,data):
        group_crm_id = data.get("group_crm_id")

        step_obj = await self._change_step_status(main_data=data)

        event = {
            'type': 'send_customer_list',
            "group_crm_id":group_crm_id
        }

        await self.channel_layer.group_send(
            f"{group_crm_id}_gp_group_crm",
            event
        )

    @sync_to_async
    def _change_step_status(self,main_data):

        step = int(main_data['step'])
        customer_obj = CustomerUser.objects.get(id=main_data['customer_id'])
        step_obj = None
        for step_item in customer_obj.label.label_step.steps.all():
            if step_item.step == step:
                step_obj = step_item

        new_step_customer = CustomerStep.objects.create(
            customer=customer_obj,
            label=customer_obj.label,
            step=step_obj
        )
        return new_step_customer

    async def send_customer_list(self,event):
        serializer_data = await self._customer_list_serializer(group_crm_id=event['group_crm_id'])
        await self.send(json.dumps(
            {
                "data_type": "customer_list",
                "data": serializer_data
            }
        ))
    async def customer_list_handler(self,data):
        group_crm_id=data.get("group_crm_id")
        customer_data = await self._customer_list_serializer(group_crm_id=group_crm_id)

        payload = {
            'data_type': 'customer_list',
            'data': customer_data,
        }
        await self.send_json(payload)
    @sync_to_async
    def _get_user_permission(self):
        workspace= self.workspace_obj

        if self.user == workspace.owner:
            return True
        workspace_member =WorkspaceMember.objects.get(user_account = self.user,workspace=workspace)
        for permission in workspace_member.permissions.all():
            if permission.permission_name == "crm":
                if permission.permission_type == "manager":
                    return True
                else:
                    return False
    @sync_to_async
    def _customer_list_serializer(self,group_crm_id):

        user_permission = self._get_user_permission()
        if user_permission:
            customer_objs = CustomerUser.objects.filter(group_crm_id=group_crm_id, is_followed=False)
        else:
            customer_objs = CustomerUser.objects.filter(group_crm_id=group_crm_id, is_followed=False,
                                                        user_account=self.user)
        data_list = []

        for customer_obj in customer_objs:
            not_exists = True
            try:
                for data in data_list:
                    if data['label_id'] == customer_obj.label.id:
                        data['customer_list'].append(CustomerSmallSerializer(customer_obj).data)
                        not_exists = False
                        break
                if not_exists:
                    data_list.append({
                        "label_id": customer_obj.label.id,
                        "color": customer_obj.label.color,
                        "title": customer_obj.label.title,
                        "steps": LabelStepSerializer(customer_obj.label.label_step.steps.all(), many=True).data,
                        "group_crm_id": group_crm_id,
                        "customer_list": [CustomerSmallSerializer(customer_obj).data]
                    })

            except:
                pass

        label_objs = Label.objects.filter(group_crm_id=group_crm_id).order_by("-id")
        for label in label_objs:
            not_exists = True
            for data in data_list:
                if data['label_id'] == label.id:
                    not_exists = False
                    break
            if not_exists:
                data_list.append({

                    "label_id": label.id,
                    "color": label.color,
                    "title": label.title,
                    "group_crm_id": group_crm_id,
                    "steps": LabelStepSerializer(label.label_step.steps.all(), many=True).data,
                    "customer_list": []
                })
        data = sorted(data_list, key=lambda x: x["label_id"])
        return data
    #Crm Customer End


    # Project Task Begin

    #Project Message Begin
    @sync_to_async
    def _all_message_serializer(self,page_number,project_id,per_page_count=None):

        message_objs = ProjectMessage.objects.filter(project_id=project_id).order_by("-id")
        if per_page_count:
            pagination_data = pagination(query_set=message_objs,page_number=page_number,per_page_count=per_page_count)
        else:
            pagination_data = pagination(query_set=message_objs,page_number=page_number)


        pagination_data['current_page'] = page_number
        pagination_data['list'] = ProjectMessageSerializer(pagination_data['list'],many=True,context={"user":self.user}).data
        pagination_data['project_id'] = project_id
        return pagination_data
    async def read_all_messages(self,data):
        project_id = data.get("project_id")
        try:

            page_number= data.get("page_number",1)
            per_page_count = data.get("per_page_count",None)
        except:
            per_page_count = None
            page_number = 1

        message_data = await self._all_message_serializer(project_id=project_id,page_number=page_number,per_page_count=per_page_count)
        await self.send_json(
            {
                "data_type": "all_messages",
                "data": message_data
            }
        )
    @sync_to_async
    def _create_a_message(self,data):
        project_id = data.get("project_id")


        data['creator_id'] = self.user.id
        serializer_data =ProjectMessageSerializer(data=data,context={"user":self.user})
        if serializer_data.is_valid():
            message_obj = serializer_data.save()
            return {
                "status":True,
                "data":{
                    "message_id":message_obj.id
                }
            }

        return {
            "status":False,
            "data":serializer_data.errors
        }
    async def create_a_message_handler(self,data):
        project_id = data.get("project_id")
        message_data = await self._create_a_message(data=data)
        if message_data['status']:
            event = {
                "type": "send_a_message",

                "message_id": message_data['data']['message_id']
            }
            project_group_name = f"{project_id}_gp_project"
            await self.channel_layer.group_send(
                project_group_name,
                event
            )

        else:
            await self.send_json(
                {
                    "data_type": "Validation Error",
                    "data": message_data['data']
                }
            )
    @sync_to_async
    def _one_message_serializer(self,message_id):
        message_obj = get_object_or_404(ProjectMessage,id=message_id)
        serializer_data = ProjectMessageSerializer(message_obj,context={"user":self.user})
        return serializer_data.data
    async def send_a_message(self,event):

        message_data = await self._one_message_serializer(message_id=event['message_id'])
        await self.send_json(
            {
                "data_type": "send_a_message",
                "data": message_data

            }
        )
    @sync_to_async
    def _edit_a_message(self,data):

        message_obj = get_object_or_404(ProjectMessage,id=data['message_id'])
        message_obj.body = data['body']
        message_obj.save()
        return {
            "status":True,
            "data":{
                "message_id":message_obj.id
            }
        }
    async def edit_message_handler(self,data):
        project_id = data.get("project_id")
        message_data = await self._edit_a_message(data=data)
        event = {
            "type": "send_a_message",

            "message_id": message_data['data']['message_id']
        }
        project_group_name = f"{project_id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )

    #Project Message End
    async def handle_task_status(self, data):
        """Handle main task status changes"""
        task = await sync_to_async(get_object_or_404)(Task, id=data['task_id'])

        if not self._has_admin_access():
            raise PermissionDenied("Access denied")

        task.done_status = data['done_status']
        await sync_to_async(task.save)()

        event = {
            "type": "send_event_task_list",

            "project_id": task.project.id
        }
        project_group_name = f"{task.project.id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )
    async def handle_subtask_status(self, data):
        """Handle subtask status changes"""

        # Fetch subtask synchronously
        subtask = await sync_to_async(
            lambda: CheckList.objects.select_related("responsible_for_doing").get(id=data['sub_task_id']),
            thread_sensitive=True)()

        # Fetch user synchronously
        responsible_user = await sync_to_async(lambda: subtask.responsible_for_doing, thread_sensitive=True)()
        task_obj = await  sync_to_async(lambda: subtask.task, thread_sensitive=True)()
        if responsible_user != self.user:
            raise PermissionDenied("Access denied")

        # Update status
        subtask.status = data['status']
        await sync_to_async(subtask.save, thread_sensitive=True)()

        event = {
            "type": "send_one_task",
            "task_id": task_obj.id,
        }
        project_group_name = f"{task_obj.project.id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )

    @sync_to_async
    def _move_a_task_logic(self,data):
        category_id = data.get("category_id")
        task_id = data.get("task_id")
        orders_task=data.get("orders_task")
        category = get_object_or_404(CategoryProject,id=category_id)
        task = get_object_or_404(Task,id=task_id)
        task.category_task=category
        task.save()
        for order_data in orders_task:

            task_obj = Task.objects.get(id=orders_task['task_id'])
            task_obj.order= order_data['order']
            task_obj.save()
        return task
    async def handle_move_task(self, data):
        task_obj = await self._move_a_task_logic(data=data)


        event = {
            "type":"send_one_task",
            "task_id":data['task_id'],
        }
        project_group_name = f"{task_obj.project.id}_gp_project"
        await self.channel_layer.group_send(
            project_group_name,
            event
        )


    async def send_one_task(self, event):


        task_data = await self._one_task_serializer(task_id=event['task_id'])

        await self.send_json({
            "data_type": "get_a_task",
            "data": task_data
        })

    @sync_to_async
    def _one_task_serializer(self,task_id):
        task_obj = Task.objects.get(id=task_id)
        task_data = {
            "category_id": task_obj.category_task.id,
            "color": task_obj.category_task.color_code,
            "title": task_obj.category_task.title,
            "task_data": TaskSerializer(task_obj).data
        }
        return  task_data
    async def handle_task_list(self, data):
        project_id = data.get("project_id")



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

    async def send_event_task_list(self, event):
        project_id = event['project_id']
        """Handler for group send events"""
        await self.send_json({
            "data_type": "task_list",
            "data": await self._main_serializer_data(project_id)
        })
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


    # Project Task End