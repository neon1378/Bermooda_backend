import json

from .serializers import CustomerSmallSerializer,LabelStepSerializer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from UserManager.models import UserAccount
from .models import CustomerUser, GroupCrm, Label
from dotenv import load_dotenv
import  os


load_dotenv()


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
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        command= data['command']
        custommer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj)
        if command == "customer_list":
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
    def send_data(self,event):
        custommer_objs = CustomerUser.objects.filter(group_crm=self.group_crm_obj)
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