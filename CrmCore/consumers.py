import json

from .serializers import CustomerSmallSerializer,LabelStepSerializer,GroupCrmMessageSerializer
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from UserManager.models import UserAccount
from .models import CustomerUser, GroupCrm, Label, CustomerStep,GroupCrmMessage
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
import  os
from core.widgets import pagination
from asgiref.sync import sync_to_async
from WorkSpaceManager.models import WorkspaceMember


load_dotenv()


class CustomerTaskMain(AsyncWebsocketConsumer):

    @sync_to_async
    def _get_group_crm_obj(self,group_crm_id):
        group_crm_obj = GroupCrm.objects.get(id=group_crm_id)
        return group_crm_obj


    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        await self.accept()
        self.group_crm_id = self.scope['url_route']['kwargs']['group_crm_id']
        self.group_crm_obj = await self._get_group_crm_obj(group_crm_id=self.group_crm_id)


        await self.channel_layer.group_add(
            f"{self.group_crm_id}_crm", self.channel_name
        )
        await self.send_initial_data()

    async def send_initial_data(self):
        group_message_data = await self._all_message_serializer(page_number=1)
        await self.send(json.dumps({
            "data_type":"all_messages",
            "data":group_message_data
        }))
        customer_user_data = await self._customer_list_serializer()
        await self.send(json.dumps(
            {
                "data_type": "customer_list",
                "data": customer_user_data
            }
        ))
    @sync_to_async
    def _one_message_serializer(self,message_id):
        message_obj = get_object_or_404(GroupCrmMessage,id=message_id)
        serializer_data = GroupCrmMessageSerializer(message_obj,context={"user":self.user})
        return serializer_data.data

    @sync_to_async
    def _all_message_serializer(self,page_number,per_page_count=None):
        message_objs = GroupCrmMessage.objects.filter(group_crm=self.group_crm_obj).order_by("-id")
        if per_page_count:
            pagination_data = pagination(
                query_set=message_objs,
                page_number=page_number,
                per_page_count=per_page_count
            )
        else:
            pagination_data = pagination(
                query_set=message_objs,
                page_number=page_number,

            )
        pagination_data["list"] = GroupCrmMessageSerializer(pagination_data["list"],many=True,context={"user":self.user}).data
        pagination_data['group_crm_id'] = self.group_crm_obj.id
        return pagination_data


    @sync_to_async
    def _a_customer_serializer(self,customer_id):
        customer_obj = CustomerUser.objects.get(id=customer_id)
        serializer_data =CustomerSmallSerializer(customer_obj).data
        return serializer_data

    @sync_to_async
    def _customer_list_serializer(self):
        user_permission =self._get_user_permission()
        if user_permission:
            customer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj, is_followed=False)
        else:
            customer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj, is_followed=False,
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
                        "group_crm_id":self.group_crm_obj.id,
                        "customer_list": [CustomerSmallSerializer(customer_obj).data]
                    })

            except:
                pass

        label_objs = Label.objects.filter(group_crm_id=self.group_crm_id).order_by("-id")
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
                    "group_crm_id":self.group_crm_obj.id,
                    "steps": LabelStepSerializer(label.label_step.steps.all(), many=True).data,
                    "customer_list": []
                })
        data = sorted(data_list, key=lambda x: x["label_id"])
        return data
    async def read_all_messages(self,data):
        try:
            main_data = data.get("data",None)
            page_number= main_data.get("page_number",1)
            per_page_count = main_data.get("per_page_count",None)
        except:
            per_page_count = None
            page_number = 1
        message_data = await self._all_message_serializer(page_number=page_number,per_page_count=per_page_count)
        await self.send(json.dumps({
            "data_type":"all_messages",
            "data":message_data
        }))
    async def send_a_message(self,event):

        message_data = await self._one_message_serializer(message_id=event['message_id'])
        await self.send(json.dumps({
            "data_type":"send_a_message",
            "data":message_data

        }))

    @sync_to_async
    def _edit_a_message(self,data):
        main_data= data['data']
        message_obj = get_object_or_404(GroupCrmMessage,id=main_data['message_id'])
        message_obj.body = main_data['body']
        message_obj.save()
        return {
            "status":True,
            "data":{
                "message_id":message_obj.id
            }
        }
    async def edit_message(self,data):
        message_data = await self._edit_a_message(data=data)

        await self.broadcast_event({
            "type": "send_a_message",
            "message_id": message_data['data']['message_id']

        })
    @sync_to_async
    def _create_a_message(self,data):
        main_data = data['data']
        main_data['group_crm_id'] = self.group_crm_obj.id
        main_data['creator_id'] = self.user.id
        serializer_data =GroupCrmMessageSerializer(data=main_data)
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
    async def create_a_message(self,data):
        message_data = await self._create_a_message(data=data)
        if message_data['status']:
            await self.broadcast_event({
                "type": "send_a_message",
                "message_id": message_data['data']['message_id']

            })
        else:
            await self.send(json.dumps({
                "data_type":"Validation Error",
                "data":message_data['data']
            }))

    async def broadcast_event(self, event):
        """Helper method for broadcasting events to group"""
        await self.channel_layer.group_send(
            f"{self.group_crm_id}_admin",
            event
        )

    @sync_to_async
    def _get_user_permission(self):
        workspace= self.group_crm_obj.workspace
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

    @sync_to_async
    def _change_customer_is_followed(self,main_data):
        customer_id = main_data['customer_id']
        customer_obj = get_object_or_404(CustomerUser, id=customer_id)
        customer_obj.is_followed = main_data['is_followed']
        customer_obj.save()
        return customer_obj

    @sync_to_async
    def _move_a_customer(self,main_data):

        customer_obj = CustomerUser.objects.get(id=main_data['customer_id'])

        label_obj = Label.objects.get(id=main_data['label_id'])
        customer_obj.label = label_obj

        customer_obj.save()
        for order_data in main_data['customer_orders']:
            customer_order = CustomerUser.objects.get(id=order_data['customer_id'])
            customer_order.order = order_data['order']
            customer_order.save()

        return customer_obj
    async def send_customer_list(self,event):
        serializer_data = await self._customer_list_serializer()
        await self.send(json.dumps(
            {
                "data_type": "customer_list",
                "data": serializer_data
            }
        ))

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        data = json.loads(text_data)
        command = data.get('command')
        print(data)
        if command == 'customer_list':
            serializer_data = await self._customer_list_serializer()
            payload = {
                'data_type': 'customer_list',
                'data': serializer_data,
            }
            await self.send(json.dumps(payload))

        elif command == 'change_step_status':
            step_obj = await self._change_step_status(main_data=data['data'])
            event = {'type': 'send_customer_list'}
            await self.channel_layer.group_send(
                f"{self.group_crm_id}_crm",
                event
            )

        elif command == 'move_a_customer':
            customer_obj = await self._move_a_customer(main_data=data['data'])
            event = {'type': 'send_customer_list'}
            await self.channel_layer.group_send(
                f"{self.group_crm_id}_crm",
                event
            )

        elif command == 'change_is_followed':
            customer_obj = await self._change_customer_is_followed(main_data=data['data'])
            event = {'type': 'send_data'}
            await self.channel_layer.group_send(
                f"{self.group_crm_id}_crm",
                event
            )

        elif command == 'read_all_messages':
            await self.read_all_messages(data=data)

        elif command == 'create_a_message':
            await self.create_a_message(data=data)

        elif command == 'edit_message':
            await self.edit_message(data=data)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"{self.group_crm_id}_crm",
            self.channel_name
        )

