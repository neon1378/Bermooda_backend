import json

from .serializers import CustomerSmallSerializer,LabelStepSerializer
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from UserManager.models import UserAccount
from .models import CustomerUser, GroupCrm, Label, CustomerStep
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
import  os
from asgiref.sync import sync_to_async
from WorkSpaceManager.models import WorkspaceMember


load_dotenv()


class CustomerTaskMain(AsyncWebsocketConsumer):

    @sync_to_async
    def _get_group_crm_obj(self,group_crm_id):
        group_crm_obj = get_object_or_404(GroupCrm,id=group_crm_id)
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
        serializer_data = await self._customer_list_serializer()
        await self.send(json.dumps(
            {
                "data_type": "customer_list",
                "data": serializer_data
            }
        ))
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
                        not_exsit = False
                        break
                if not_exists:
                    data_list.append({
                        "label_id": customer_obj.label.id,
                        "color": customer_obj.label.color,
                        "title": customer_obj.label.title,
                        "steps": LabelStepSerializer(customer_obj.label.label_step.steps.all(), many=True).data,

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
                    "steps": LabelStepSerializer(label.label_step.steps.all(), many=True).data,
                    "customer_list": []
                })
        data = sorted(data_list, key=lambda x: x["label_id"])
        return data
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
        if text_data:
            data = json.loads(text_data)
            command = data['command']
            if command == "customer_list":
                serializer_data = await self._customer_list_serializer()
                await self.send(json.dumps(
                    {
                        "data_type": "customer_list",
                        "data": serializer_data
                    }
                ))
            elif command == "change_step_status":
                step_obj = await  self._change_step_status(main_data =data['data'])
                event = {
                    "type": "send_customer_list"
                }

                await self.channel_layer.group_send(
                    f"{self.group_crm_id}_crm", event
                )
            elif command ==  "move_a_customer":

                customer_obj = await self._move_a_customer(main_data=data['data'])
                event = {
                    "type": "send_customer_list"
                }
                await self.channel_layer.group_send(
                    f"{self.group_crm_id}_crm", event
                )
            elif command == "change_is_followed":
                customer_obj = await self._change_customer_is_followed(main_data=data['data'])
                event = {
                    "type": "send_data"
                }
                await self.channel_layer.group_send(
                    f"{self.group_crm_id}_crm", event
                )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"{self.group_crm_id}_crm",
            self.channel_name
        )
class CustomerTask(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.accept()
        else:
            self.close(code=1)
        self.group_crm_id = self.scope['url_route']['kwargs']['group_crm_id']

        self.group_crm_obj = GroupCrm.objects.get(id=self.group_crm_id)

        async_to_sync(self.channel_layer.group_add)(
            f"{self.group_crm_id}_crm",self.channel_name
        )

    def send_a_customer(self,event):
        customer_obj = CustomerUser.objects.get(id=event['customer_id'])
        serializer_data = CustomerSmallSerializer(customer_obj)
        self.send(json.dumps(
            {
                "data_type":"send_a_customer",
                "data":serializer_data.data
            }
        ))


    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        command= data['command']

        if command == "customer_list":
            if self.get_user_permission():
                custommer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj,is_followed=False)
            else:
                custommer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj,is_followed=False,user_account=self.user)

            data_list = []

            for custommer_obj in custommer_objs:
                not_exsit = True
                try:
                    for data in data_list:
                        if data['label_id'] == custommer_obj.label.id:
                            data['customer_list'].append(CustomerSmallSerializer(custommer_obj).data)
                            not_exsit = False
                            break
                    if not_exsit:
                        data_list.append({
                            "label_id": custommer_obj.label.id,
                            "color": custommer_obj.label.color,
                            "title": custommer_obj.label.title,
                            "steps":LabelStepSerializer(custommer_obj.label.label_step.steps.all(),many=True).data,



                            "customer_list": [CustomerSmallSerializer(custommer_obj).data]
                        })

                except:
                    pass

            label_objs = Label.objects.filter(group_crm_id=self.group_crm_id).order_by("-id")
            for label in label_objs:
                not_exsit = True
                for data in data_list:
                    if data['label_id'] == label.id:
                        not_exsit = False
                        break
                if not_exsit:
                    data_list.append({

                        "label_id": label.id,
                        "color": label.color,
                        "title": label.title,
                        "steps": LabelStepSerializer(label.label_step.steps.all(), many=True).data,
                        "customer_list": []
                    })
            data = sorted(data_list, key=lambda x: x["label_id"])

            self.send(json.dumps(
                {
                    "data_type":"customer_list",
                    "data":data
                }
            ))
        elif command == "change_step_status":
            main_data = data['data']
            step = int(main_data['step'])
            customer_obj = CustomerUser.objects.get(id=main_data['customer_id'])
            step_obj = None
            for step_item in customer_obj.label.label_step.steps.all():
                if step_item.step == step:
                    step_obj = step_item

            new_step_customer =CustomerStep.objects.create(
                customer =customer_obj,
                label= customer_obj.label,
                step=step_obj
            )
            event = {
                "type":"send_data"
            }
            async_to_sync(self.channel_layer.group_send)(
                f"{self.group_crm_id}_crm",event

            )
        elif command == "move_a_customer":
            main_data = data['data']
            customer_obj = CustomerUser.objects.get(id=main_data['customer_id'])

            label_obj = Label.objects.get(id=main_data['label_id'])
            customer_obj.label= label_obj

            customer_obj.save()
            for order_data in main_data['customer_orders']:
                customer_order = CustomerUser.objects.get(id=order_data['customer_id'])
                customer_order.order =order_data['order']
                customer_order.save()
            event = {
                "type":"send_data"
            }
            async_to_sync(self.channel_layer.group_send)(
                f"{self.group_crm_id}_crm",event

            )
        elif command == "change_is_followed":
            main_data = data['data']

            customer_id = main_data['customer_id']
            customer_obj = get_object_or_404(CustomerUser,id=customer_id)
            customer_obj.is_followed = main_data['is_followed']
            customer_obj.save()
            event = {
                "type":"send_data"
            }
            async_to_sync(self.channel_layer.group_send)(
                f"{self.group_crm_id}_crm",event

            )

    def get_user_permission(self):
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

    def send_data(self,event):
        if self.get_user_permission():
            custommer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj,is_followed=False)
        else:
            custommer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj,user_account=self.user,is_followed=False)
        data_list = []
        for custommer_obj in custommer_objs:
            not_exsit = True
            try:
                for data in data_list:
                    if data['label_id'] == custommer_obj.label.id:
                        data['customer_list'].append(CustomerSmallSerializer(custommer_obj).data)
                        not_exsit = False
                        break
                if not_exsit:
                    data_list.append({
                        "label_id": custommer_obj.label.id,
                        "color": custommer_obj.label.color,
                        "title": custommer_obj.label.title,
                        "steps": LabelStepSerializer(custommer_obj.label.label_step.steps.all(), many=True).data,
                        "customer_list": [CustomerSmallSerializer(custommer_obj).data]
                    })
            except:
                pass

        label_objs = Label.objects.filter(group_crm_id=self.group_crm_id)
        for label in label_objs:
            not_exsit = True
            for data in data_list:
                if data['label_id'] == label.id:
                    not_exsit = False
                    break
            if not_exsit:
                data_list.append({
                    "label_id": label.id,
                    "color": label.color,
                    "title": label.title,
                    "steps": LabelStepSerializer(label.label_step.steps.all(), many=True).data,
                    "customer_list": []
                })
        data = sorted(data_list, key=lambda x: x["label_id"])
        self.send(json.dumps(
            {
                "data_type": "customer_list",
                "data": data
            }
        ))

    def disconnect(self, code=None):

        async_to_sync(self.channel_layer.group_discard)(
            f"{self.group_crm_id}_crm",
            self.channel_name
        )
        self.close(code=0)