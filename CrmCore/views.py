from celery.worker.state import reserved_requests
from django.core.paginator import Paginator
from django.shortcuts import render
from rest_framework.permissions import AllowAny,IsAuthenticated,DjangoModelPermissions
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import *
from core.widgets import pagination
from datetime import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .serializers import *
from rest_framework import status
from core.permission import IsWorkSpaceMemberAccess
from WorkSpaceManager.models import WorkSpace,WorkspaceMember
from UserManager.models import UserAccount
from rest_framework.permissions import BasePermission
from core.widgets import pagination
# Create your views here.
from core.permission import IsAccess
from dotenv import load_dotenv
import os
from core.widgets import  persian_to_gregorian
from channels.layers import get_channel_layer
from django.db import transaction
from core.widgets import  ReusablePaginationMixin,create_reminder
load_dotenv()




def create_reminde_a_customer(customer):
    if customer.main_date_time_to_remember:
        title = "یاد آوری وظیفه"

        sub_title = f"وقت پیگیری  {customer.fullname_or_company_name} هست "
        create_reminder(related_instance=customer, remind_at=customer.main_date_time_to_remember, title=title, sub_title=sub_title)

class CrmDepartmentManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,department_id=None):

        if department_id:
            department_obj = get_object_or_404(CrmDepartment,id=department_id)
            serializer_data = CrmDepartmentSerializer(department_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)

        department_objs= CrmDepartment.objects.filter(workspace=workspace_obj)
        serializer_data = CrmDepartmentSerializer(department_objs,many=True)


        return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
    def post(self,request):
        request.data['workspace_id'] = request.user.current_workspace_id 
        request.data['manager_id'] = request.user.id
        serializer_data = CrmDepartmentSerializer(data=request.data)
        data= request.data

       



        if serializer_data.is_valid():
            serializer_data.save()

            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"validation error",
            "data": serializer_data.errors
        })
    def put(self,request,department_id):
        department_obj = get_object_or_404(CrmDepartment,id=department_id)
        request.data['workspace_id'] = department_obj.workspace.id
        request.data['manager_id'] = department_obj.manager.id
        serializer_data = CrmDepartmentSerializer(data=request.data,instance=department_obj)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"validation error",
            "data":serializer_data.errors
        })

    def delete(self,request,department_id):
        department_obj = get_object_or_404(CrmDepartment,id=department_id)
        department_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    




class CategoryManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,category_id=None):
        if category_id:
            category_obj = get_object_or_404(Category,id=category_id)
            serializer_data = CategorySerializer(category_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        workspace_id = request.user.current_workspace_id
        group_crm_id = request.GET.get("group_crm_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)

        category_objs = Category.objects.filter(workspace=workspace_obj,group_crm_id=group_crm_id)
        serializer_data = CategorySerializer(category_objs,many=True)

        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":serializer_data.data
        })
    def post (self,request):

        request.data['workspace_id'] = request.user.current_workspace_id
        serializer_data =CategorySerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()

            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت ثبت شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.errors
        })
    def put(self,request,category_id):
        data= request.data
        category_obj = get_object_or_404(Category,id=category_id)
        request.data['group_crm_id'] = category_obj.group_crm.id
        request.data['workspace_id'] = category_obj.workspace.id
        serializer_data = CategorySerializer(instance=category_obj,data=request.data)
        if serializer_data.is_valid():
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.errors
        })
    def delete(self,request,category_id):
        category_obj = get_object_or_404(Category,id=category_id)
        category_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class LabelMangaer(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    channel_layer = get_channel_layer()
    def get(self,request,label_id=None):
        if label_id:
            label_obj = get_object_or_404(Label,id=label_id)
            serializer_data = LabelSerializer(label_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        group_crm_id = request.GET.get("group_id")
        group_obj = get_object_or_404(GroupCrm,id=group_crm_id)
        label_objs = Label.objects.filter(group_crm= group_obj)
        serializer_data = LabelSerializer(label_objs,many=True)

        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":serializer_data.data
        })
    def post (self,request):



        serializer_data =LabelSerializer(data=request.data)
        if serializer_data.is_valid():
            label_obj = serializer_data.save()



            event = {
                'type': 'send_customer_list',
                "group_crm_id": label_obj.group_crm.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{label_obj.group_crm.id}_gp_group_crm", event)
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت ثبت شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"ناموفق",
            "data":serializer_data.errors
        })
    def put(self,request,label_id):
        data= request.data
        label_obj = get_object_or_404(Label,id=label_id)
        workspace_id = data.pop("workspace_id",None)
        serializer_data =LabelSerializer(data=request.data,instance=label_obj)
        if serializer_data.is_valid():
            serializer_data.save()


            event = {
                'type': 'send_customer_list',
                "group_crm_id": label_obj.group_crm.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{label_obj.group_crm.id}_gp_group_crm", event)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": True,
            "message": "error ",
            "data": serializer_data.errors
        })
    def delete(self,request,label_id):
        label_obj = get_object_or_404(Label,id=label_id)
        first_label =Label.objects.filter(group_crm=label_obj.group_crm).last()
        if first_label.id == label_obj.id:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={
                "status":False,
                "message":"لیست پیشفرض را نمیتوانید حذف کنید",
                "data":{}
            })
        group_crm_id = label_obj.group_crm.id
        label_obj.delete()


        event = {
            'type': 'send_customer_list',
            "group_crm_id": group_crm_id
        }

        async_to_sync(self.channel_layer.group_send)(f"{group_crm_id}_gp_group_crm", event)
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class ReportManager(APIView):

    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]
    def add_file_urls(self, report_obj):
   
        base_url = os.getenv("BASE_URL")
        data = f"{base_url}{report_obj.main_file.file.url}" if report_obj.main_file else ""
           
   
        return data
    def get (self,request,report_id=None):
        if report_id:
            report_obj = get_object_or_404(Report,id=report_id)
            response_data = {
                "payment_time_to_remember":report_obj.payment_time_to_remember,
                "payment_date_to_remember":report_obj.payment_date_to_remember,
                "id":report_obj.id,
                "invoice_id":report_obj.invoice_id,
                "label_id": report_obj.label_id,
                "report_type":report_obj.report_type,
                "description":report_obj.description,
                "file_url":self.add_file_urls(report_obj=report_obj),
                "self":request.user == report_obj.author,
                
                "jtime":report_obj.jtime(),
                
                  "file_urls":[
                    
                    f"{base_url}{file.file.url}" for file in report_obj.main_file.all()
                ],
            }
            if report_obj.author:
                    response_data['author']=report_obj.author.fullname
                    response_data['avatar_url'] = report_obj.author.avatar_url()
            else:
                    response_data['author'] = ""
                    response_data['avatar_url'] = ""


            return Response (status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":response_data
            })

        customer_obj = get_object_or_404(CustomerUser,id=request.GET.get("customer_id"))
        report_objs = customer_obj.report.all().order_by("-id")
        response_data=[]
        base_url= os.getenv("BASE_URL")
        for report_obj in report_objs:
        
                dic = {
        
 
                "jtime":report_obj.jtime(),
      
                
                "file_urls":[
                    
                    f"{base_url}{file.file.url}" for file in report_obj.main_file.all()
                ],
                 "id":report_obj.id,
                 "description":report_obj.description,
                 "self":request.user == report_obj.author,


                 }
 
                if report_obj.author:
                    try:
                        dic['avatar_url']=report_obj.author.avatar_url()
                        dic['author']=report_obj.author.fullname 
                    except:
                        dic['author'] = ""
                        dic['avatar_url']=''



                else:
                    dic['author'] = ""
                response_data.append(dic)
         
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":response_data
        })
    def post (self,request):
        data= request.data
        customer_obj = get_object_or_404(CustomerUser,id=data['customer_id'])
        file_id_list = data.get("file_id_list",[])        





        

        new_report = Report(
            description = data['description'],
            
            author=request.user,
  
        )
        new_report.save()
   
   
            
        for file_id in file_id_list:
            main_file_obj = MainFile.objects.get(id=file_id)
            main_file_obj.its_blong=True
            main_file_obj.save()
            new_report.main_file.add(MainFile.objects.get(id=file_id))
            
        new_report.save()
        base_url = os.getenv("BASE_URL")
        customer_obj.report.add(new_report)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت ثبت شد",
            "data":{

                "description":new_report.description,

                "jtime":new_report.jtime(),
                "file_urls":[
                    
                    f"{base_url}{file.file.url}" for file in new_report.main_file.all()
                ]

            }
        })
    

class GroupCrmManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceMemberAccess]
    def paginate_queryset(self,page_number,queryset,workspace_obj):


        # Set up custom pagination
        paginator = Paginator(queryset, 20)  # Set items per page

        # Check if the requested page exists
        if int(page_number) > paginator.num_pages:
            return {
                "count": paginator.count,
                "next": None,
                "previous": None,
                "data": []
            }

        # Get the page
        page = paginator.get_page(page_number)
        serializer_data=GroupCrmSerializer(page.object_list,many=True)
        for group in serializer_data.data:
            for member in group["members"]:
                if member["id"] == workspace_obj.owner.id:
                    member["type"] = "manager"
                else:
                    workspace_member = WorkspaceMember.all_objects.filter(
                        user_account_id=member["id"], workspace=workspace_obj
                    ).first()  # Use `.first()` to avoid exceptions
                    member['fullname'] = workspace_member.fullname
                    if workspace_member:
                        permission = next(
                            (perm.permission_type for perm in workspace_member.permissions.all() if
                             perm.permission_name == "crm"),
                            None,
                        )
                        if permission:
                            member["type"] = permission
        return {
            "count": paginator.count,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": serializer_data.data
        }

    def get(self, request, group_id=None):

        workspace_id = request.user.current_workspace_id
        workspace_obj = get_object_or_404(WorkSpace, id=workspace_id)
        page = request.GET.get("page",1)
        # Fetch single group if `group_id` is provided
        if group_id:
            group_obj = get_object_or_404(GroupCrm, id=group_id)
            if request.user == workspace_obj.owner or request.user in group_obj.members.all():
                serializer_data = GroupCrmSerializer(group_obj)




                group_data = serializer_data.data
                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "status": True,
                        "message": "success",
                        "data": group_data,
                        
                    },
                )
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"status": False, "message": "access denied"},
            )

        # Fetch all groups for the workspace
        department_id = request.GET.get("department_id",None)
        if workspace_obj.owner == request.user:
            group_objs = GroupCrm.objects.filter(workspace=workspace_obj,department_id=department_id).order_by("-id")
        else:

                group_list = GroupCrm.objects.filter(workspace=workspace_obj,department_id=department_id).order_by("-id")
                group_objs = []
                for group in group_list:
                    if request.user in group.members.all():
                        group_objs.append(group)
                

        group_data = self.paginate_queryset(page_number=page,queryset=group_objs,workspace_obj=workspace_obj)

        return Response(
            status=status.HTTP_200_OK,
            data={
                "status": True,
                "message": "success",
                "data": group_data,
            },
        )

    def create_crm_label(self,group_crm_obj):

        label_list = [
            {
                "title": "کشف مشتری ",
                "color_code": "#E82BA3",
                "order":1,
                "steps":[
                    {
                        "title":"جذب",
                        "step":1,
                    },
                    {
                        "title":"جمع‌آوری اطلاعات",
                        "step":2,
                    },
                    {
                        "title":"تماس اولیه ",
                        "step":3,
                    },

                    {
                        "title":"تکمیل اطلاعات ",
                        "step":4,
                    },
                    {
                        "title": "تعیین وضعیت",
                        "step": 5,
                    },
                ]

            },
            {
                "title": "معرفی محصول/ خدمات",
                "color_code": "#DB4646",
                "order": 2,
                "steps":[
                    {
                        "title": "نیازسنجی",
                        "step": 1,
                    },
                    {
                        "title": "پیشنهاد اولیه",
                        "step": 2,
                    },
                    {
                        "title": "ارائه محصول / خدمات",
                        "step": 3,
                    },

                    {
                        "title": "  نیاز ها و ابهامات ",
                        "step": 4,
                    },
                    {
                        "title": "بازخورد",
                        "step": 5,
                    },
                ]
            },

            {
                "title": "پیشنهاد / ارزیابی",
                "color_code": "#02C875",
                "order": 3,
                "steps": [
                    {
                        "title": "تهیه پیشنهاد",
                        "step": 1,
                    },
                    {
                        "title": "مذاکره و سفارشی‌سازی ",
                        "step": 2,
                    },
                    {
                        "title": "آزمایش یا تست محصول",
                        "step": 3,
                    },


                    {
                        "title": "پیگیری مشتری",
                        "step": 4,
                    },
                ]
            },

            {
                "title": "فاکتور / قرارداد",
                "color_code": "#04C4B7",
                "order": 4,
                "steps": [
                    {
                        "title": "تهیه پیش‌ فاکتور/قرارداد   ",
                        "step": 1,
                    },
                    {
                        "title": "نهایی‌سازی فاکتور/قرارداد ",
                        "step": 2,
                    },
                    {
                        "title": "تایید پرداخت اولیه   ",
                        "step": 3,
                    },

                    {
                        "title": "هماهنگی برای تحویل    ",
                        "step": 4,
                    },
                    {
                        "title": "ثبت و بایگانی مدارک ",
                        "step": 5,
                    },
                ]
            },

            {
                "title": "بسته شده",
                "color_code": "#636D74",
                "order": 5,
                "steps": [
                    {
                        "title": "تحویل محصول یا ارائه خدمت ",
                        "step": 1,
                    },
                    {
                        "title": "آموزش و مشاوه  ",
                        "step": 2,
                    },


                    {
                        "title": "پشتیبانی فروش ",
                        "step": 3,
                    },
                    {
                        "title": "نعیین وضعیت فروش مجدد ",
                        "step": 4,
                    },
                ]
            },
        ]


        for label in label_list:
            new_label_obj = Label(order=label['order'],title=label['title'], color=label['color_code'], group_crm=group_crm_obj)
            new_label_obj.save()
            new_label_step = LabelStep.objects.create(label=new_label_obj)
            for step in label['steps']:
                new_step = Step.objects.create(
                    title=step['title'],
                    step=step['step'],
                    label_step=new_label_step
                )



    def post(self, request):
        data = request.data
        workspace_id = request.user.current_workspace_id
        workspace_obj = get_object_or_404(WorkSpace, id=workspace_id)
        members = data.get("members", [])
        title = data.get("title")

        department_id = data.get("department_id",None)

        avatar_id = data.get("avatar_id",None)

        # Create new group
        new_group_obj = GroupCrm.objects.create(title=title,workspace=workspace_obj)
        
        new_group_obj.department_id=department_id
        new_group_obj.manager =request.user

        # Add members to the group
        is_user = True
        for member_id in members:
            if int(member_id)  == request.user.id:
                is_user= False
            user_account = get_object_or_404(UserAccount, id=member_id)
            new_group_obj.members.add(user_account)
        if is_user:
            new_group_obj.members.add(request.user)
        # Set avatar if provided
        if avatar_id:
            main_file_obj = get_object_or_404(MainFile, id=avatar_id)
            main_file_obj.its_blong = True
            main_file_obj.save()
            new_group_obj.avatar = main_file_obj
        

        new_group_obj.save()
        print(new_group_obj.members.all().count(),"@@@@")
        self.create_crm_label(group_crm_obj=new_group_obj)
            # order +=1
        group_data = GroupCrmSerializer(new_group_obj).data


        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "status": True,
                "message": "success",
                "data": group_data,
            },
        )



    def put(self,request,group_id):
        data = request.data
        group_obj = get_object_or_404(GroupCrm,id=group_id)
        workspace_id = request.user.current_workspace_id

     

        workspace_obj = get_object_or_404(WorkSpace, id=workspace_id)
        members = data.get("members", [])
        title = data.get("title")
        department_id= data.get("department_id",None)
        avatar_id = data.get("avatar_id",None)
        group_obj.title = title
        
        group_obj.department_id=department_id
        with transaction.atomic():
            group_obj.members.clear()
            if members:
                members = UserAccount.objects.filter(id__in=members)
                group_obj.members.add(*members)
        if avatar_id:
            if group_obj.avatar:
                if group_obj.avatar.id != avatar_id:
                    group_obj.avatar.delete()
                    avatar_obj= MainFile.objects.get(id=avatar_id)
                    avatar_obj.its_blong=True
                    avatar_obj.save()
            else:
                avatar_obj= MainFile.objects.get(id=avatar_id)
                avatar_obj.its_blong=True
                avatar_obj.save()
            group_obj.avatar=avatar_obj
        group_obj.save()
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"success",
            "data":GroupCrmSerializer(group_obj).data
        })
    def delete (self,request,group_id):
        data =request.data
        group_obj = get_object_or_404(GroupCrm,id=group_id)
        group_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    




@api_view(['PUT'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def change_customer_supervisor(request,customer_id):
    data=request.data
    customer_obj = get_object_or_404(CustomerUser,id=customer_id)
    user_id = data['user_id']
    current_user_acc_id =customer_obj.user_account.id
    
    user_acc_reciver = get_object_or_404(UserAccount,id=user_id)
    customer_obj.user_account = user_acc_reciver
    customer_obj.save()
   
  


    return Response(status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def change_customer_status(request,customer_id):
    data= request.data
    label_id = data.get("label_id",None)
    label_obj = get_object_or_404(Label,id=label_id)
    possibility_of_sale = data.get("possibility_of_sale",None)
    date_time_to_remember = data.get("date_time_to_remember",None)
    customer_obj = get_object_or_404(CustomerUser,id=customer_id)
    if possibility_of_sale:
        customer_obj.possibility_of_sale=possibility_of_sale
    if date_time_to_remember:
        customer_obj.date_time_to_remember =date_time_to_remember 
    if label_id:
        customer_obj.label=label_obj
    customer_obj.save()
    return Response(status=status.HTTP_202_ACCEPTED,data={
        "status":True,
        "message":"success",
        "data":{}
    })
        






@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
@api_view(['GET'])
def get_crm_group_members(request,group_id):
    workspace_id= request.user.current_workspace_id
    workspace_obj= get_object_or_404(WorkSpace,id=workspace_id)
    group_obj = get_object_or_404(GroupCrm,id=group_id)
    print(workspace_obj.id,"@@@@")
    member_list = []
    a=WorkspaceMember.objects.filter(workspace=workspace_obj)
    for item in a :
        print(item.user_account,"!!")

    for member in group_obj.members.all():
        print(member,"___")
        try:
            if workspace_obj.owner == member:
                member_list.append({
                    "id": member.id,
                    "fullname": member.username,
                    "avatar_url": member.avatar_url(),
                    "self":request.user == member
                })
            else:
                workspace_member = WorkspaceMember.all_objects.get(workspace=workspace_obj,user_account=member)

                if workspace_member.is_accepted:
                    member_list.append({
                        "id": member.id,
                        "fullname": workspace_member.fullname,
                        "avatar_url": member.avatar_url(),
                        "self":request.user == member
                    })
        except:
            pass
    
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":member_list
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def create_report_message(request,customer_id):
    customer_obj = get_object_or_404(CustomerUser,id=customer_id)
    data = request.data
    description =  data.get("description",None)
    file_id_list = data.get("file_list",[])
    new_report = Report(author=request.user)
    if description:
        new_report.description = description
    new_report.save()
    for file_id in file_id_list:
        main_file_obj = MainFile.objects.get(id=file_id)
        main_file_obj.its_blong=True
        main_file_obj.save()
        new_report.main_file.add(main_file_obj)
    customer_obj.report.add(new_report)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":{
            "id":new_report.id,
            "jtime":new_report.jtime(),
            "description":new_report.description,
            "avater_url":new_report.author.avatar_url(),
            "invoice_id":new_report.invoice_id,
            "label_id": new_report.label_id,
            "self":request.user == new_report.author,

        }
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def exist_member_in_crm(request,group_id):
    group_crm = get_object_or_404(GroupCrm,id=group_id)
    workspace_obj = WorkSpace.objects.get(id=request.user.current_workspace_id)
    user_list = []
    user_list.append(workspace_obj.owner)
    for member in WorkspaceMember.objects.filter(workspace=workspace_obj):
        if member.user_account != workspace_obj.owner:
            user_list.append(member.user_account)
    serializer_data= [
        {
            "id":user.id,
            "fullname":user.fullname,
            "avatar_url":user.avatar_url(),
            "selected": user in group_crm.members.all()
        } for user in user_list
    ]
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":serializer_data
    })


class CustomerUserView(APIView):

    permission_classes  = [IsAuthenticated,IsWorkSpaceMemberAccess]
    channel_layer = get_channel_layer()
    def get(self,request,customer_id=None):
        if customer_id:
            custommer_obj= get_object_or_404(CustomerUser,id=customer_id)
            serializer_data = CustomerSmallSerializer(custommer_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "data":"success",
                "data":serializer_data.data
            })
        group_crm_id = request.GET.get("group_crm_id",None)

        custommer_objs = CustomerUser.objects.filter(group_crm_id=group_crm_id)


        serializer_data = CustomerSmallSerializer(custommer_objs,many=True)
        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "success",
            "data": serializer_data.data
        })

    def post(self,request):
        data= request.data
        data['workspace_id'] =request.user.current_workspace_id

        data['user_account_id'] =request.user.id
        group_crm_objs = GroupCrm.objects.filter(workspace= data['workspace_id'])
        for group in group_crm_objs:
            is_customer_exists = CustomerUser.objects.filter(phone_number=data['phone_number'], group_crm=group).exists()
            if is_customer_exists:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data= {
                        "status": False,
                        "message": "شماره تلفن وارد شده در حال حاضر در کسب و کار شما وجود دارد"
                    }
                )
        serializer_data = CustomerSmallSerializer(data=request.data)
        if serializer_data.is_valid():
            customer_obj = serializer_data.save()
            customer_obj.main_date_time_to_remember = persian_to_gregorian(customer_obj.date_time_to_remember)
            customer_obj.save()
            create_reminde_a_customer(customer=customer_obj)


            event = {
                'type': 'send_customer_list',
                "group_crm_id": customer_obj.group_crm.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{customer_obj.group_crm.id}_gp_group_crm", event)
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"مشتری با موفقیت ثبت شد",
                "data":serializer_data.data
            })

        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"اطلاعات به درستی ارسال نشده است ",
            "data":serializer_data.errors
        })
    def put(self,request,customer_id):
        customer_obj = get_object_or_404(CustomerUser,id=customer_id)

        workspace_id = request.user.current_workspace_id
        request.data['workspace_id'] = workspace_id
        request.data['user_account_id'] = int(customer_obj.user_account.id)
        serializer_data = CustomerSmallSerializer(data=request.data,instance=customer_obj)
        if serializer_data.is_valid():
            updated_customer =serializer_data.save()
            updated_customer.main_date_time_to_remember = persian_to_gregorian(updated_customer.date_time_to_remember)
            updated_customer.save()



            event = {
                'type': 'send_customer_list',
                "group_crm_id": customer_obj.group_crm.id
            }

            async_to_sync(self.channel_layer.group_send)(f"{customer_obj.group_crm.id}_gp_group_crm", event)
            create_reminde_a_customer(customer=updated_customer)
            return Response(status=status.HTTP_201_CREATED, data={
                "status": True,
                "message": "مشتری با موفقیت بروزرسانی  شد",
                "data": serializer_data.data
            })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "اطلاعات به درستی ارسال نشده است ",
            "data": serializer_data.errors
        })
    def delete(self,request,customer_id):
        customer_obj = get_object_or_404(CustomerUser, id=customer_id)
        group_crm_id = customer_obj.group_crm.id
        customer_obj.delete()


        event = {
            'type': 'send_customer_list',
            "group_crm_id": group_crm_id
        }

        async_to_sync(self.channel_layer.group_send)(f"{group_crm_id}_gp_group_crm", event)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CampaignManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,campaign_id=None):
        if campaign_id:
            campaign_obj = get_object_or_404(Campaign,id=campaign_id)
            serializer_data = CampaignSerializer(campaign_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        group_crm_id = request.GET.get("group_crm_id")
        campaign_objs= Campaign.objects.filter(group_crm_id=group_crm_id,creator=request.user)
        serializer_data = CampaignSerializer(campaign_objs,many=True)
        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "success",
            "data": serializer_data.data
        })

    def post(self,request):
        request.data['creator_id'] = request.user.id
        serializer_data= CampaignSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "stauts":True,
                "message":"با موفقیت ثبت شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"validation error",
            "data":serializer_data.errors
        })

    def put (self,request,campaign_id):
        campaign_obj = get_object_or_404(Campaign,id=campaign_id)
        request.data['creator_id'] =request.user.id
        request.data['group_crm_id'] = campaign_obj.group_crm.id
        serializer_data = CampaignSerializer(instance=campaign_obj,data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_202_ACCEPTED, data={
            "status": False,
            "message": "validation error",
            "data": serializer_data.errors
        })
@api_view(['GET'])
@permission_classes([AllowAny,IsWorkSpaceMemberAccess])
def campaign_show (request,uuid):
    campaign = get_object_or_404(Campaign,uuid=uuid)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # First IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')
    if IpExist.objects.filter(ip=ip,campaign=campaign).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"ای پی وارد شده وجود دارد",
            "data":{}

        })

    serializer_data =CampaignSerializer(campaign)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":serializer_data.data
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def submit_form (request,uuid):
    data= request.data
    field_list = data.get("field_list")
    fullname= data.get("fullname",None)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # First IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')
    campaign = get_object_or_404(Campaign, uuid=uuid)
    new_campaign_form =CampaignForm(campaign=campaign,fullname=fullname)
    if IpExist.objects.filter(ip=ip,campaign=campaign).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"ای پی وارد شده وجود دارد",
            "data":{}

        })
    IpExist.objects.create(ip=ip,campaign=campaign)
    new_campaign_form.save()
    for field in field_list:
        CampaignFormData.objects.create(
            title = field['title'],
            field_type=field['field_type'],
            text = field['text'],
            campaign_form = new_campaign_form
        )


    return Response(status=status.HTTP_201_CREATED,data={
        "status":True,
        "message":"success",
        "data":{}
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def get_campaign_form(request,campaign_form_id=None):

    if campaign_form_id:
        campaign_form = get_object_or_404(CampaignForm,id=campaign_form_id)
        serializer_data =CampaignFormSerializer(campaign_form)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data
        })

    campaign_id = request.GET.get("campaign_id")
    campaign_obj =get_object_or_404(Campaign,id=campaign_id)
    campaign_form_objs = CampaignForm.objects.filter(campaign=campaign_obj)
    serializer_data = CampaignFormSerializer(campaign_form_objs,many=True)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":serializer_data.data
    })




@api_view(['POST'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def referral_the_lead(request):
    data =request.data
    campaign_form_id_list = data.get("campaign_form_id_list",[])
    group_crm_id = data.get("group_crm_id")
    group_crm_obj = get_object_or_404(GroupCrm,id=group_crm_id)
    member_id = data.get("member_id")
    member_obj = get_object_or_404(UserAccount,id= member_id)
    first_label = Label.objects.filter(group_crm = group_crm_obj).first()
    for campaign_form_id in campaign_form_id_list:
        campaign_form_obj = CampaignForm.objects.get(id=campaign_form_id)
        new_customer_user = CustomerUser(
            user_account= member_obj,
            personal_type= "حقیقی",
            label=first_label,
            fullname_or_company_name = campaign_form_obj.fullname

        )
        new_customer_user.save()
        campaign_form_obj.delete()
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"با موفقیت ارجاع داده شد",
        "data":{}
    })

def create_fake_ip (request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # First IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')
    obj  =IpAshol.objects.create(ip=ip)
    return render(request,"CrmCore/test.html")



@api_view(['POST'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def referral_customer(request,customer_id):
    data= request.data
    customer_obj = get_object_or_404(CustomerUser,id=customer_id)
    group_crm_id = data.get("group_crm_id")
    group_obj = get_object_or_404(GroupCrm,id=group_crm_id)
    last_label = Label.objects.filter(group_crm=group_obj).last()
    customer_obj.group_crm =group_obj
    customer_obj.label = last_label
    customer_obj.save()
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"با موفقیت انجام شد",
        "data":{}
    })

class CustomerArchive(APIView):
    permission_classes= [IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request):

        group_crm_id = request.GET.get("group_crm_id")
        customer_objs = CustomerUser.all_objects.filter(is_deleted=True,group_crm_id=group_crm_id)
        serializer_data = CustomerSmallSerializer(customer_objs,many=True)
        page_number = request.GET.get("page", 1)

        paginator = Paginator(customer_objs.order_by("-id"), 20)  # Set items per page

        # Check if the requested page exists
        if int(page_number) > paginator.num_pages:
            return {
                "count": paginator.count,
                "next": None,
                "previous": None,
                "data": []
            }

        # Get the page
        page = paginator.get_page(page_number)
        serializer_data = CustomerSmallSerializer(page.object_list,many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data": {
                "count": paginator.count,
                "next": page.next_page_number() if page.has_next() else None,
                "previous": page.previous_page_number() if page.has_previous() else None,
                "list": serializer_data.data
            }
        })
    def put(self,request,customer_id):
        customer_obj =CustomerUser.all_objects.get(id=customer_id)
        customer_obj.restore()
        customer_obj.save()
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"با موفقیت بازیابی شد",
            "data":CustomerSmallSerializer(customer_obj).data
        })


import jdatetime
from datetime import datetime


import jdatetime
from datetime import datetime

def persian_to_datetime(persian_date_time):
    # Handle None or empty string
    if not persian_date_time or not persian_date_time.strip():
        return None

    try:
        # Split the date and time
        date, time = persian_date_time.strip().split()
    except ValueError:
        # Handle malformed input (e.g., missing time part)
        return None

    try:
        # Parse the Persian date
        year, month, day = map(int, date.split('/'))
        # Parse the time
        hour, minute = map(int, time.split(':'))
        # Create a jdatetime object
        persian_datetime = jdatetime.datetime(year, month, day, hour, minute)
        # Convert to Gregorian datetime
        gregorian_datetime = persian_datetime.togregorian()
        return gregorian_datetime
    except (ValueError, IndexError, jdatetime.JalaliDateOutOfRangeError):
        # Handle invalid date or time format
        return None

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def my_customers(request):
    group_crm_id = request.GET.get("group_crm_id")
    customer_objs = CustomerUser.objects.filter(group_crm_id=group_crm_id,user_account=request.user)
    page_number = request.GET.get("page",1)

    paginator = Paginator(customer_objs.order_by("-id"), 20)  # Set items per page

    # Check if the requested page exists
    print()
    if int(page_number) > paginator.num_pages:
        return {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "data": []
        }

    # Get the page
    page = paginator.get_page(page_number)
    serializer_data = CustomerSmallSerializer(page.object_list, many=True).data
    for customer in serializer_data:
        print(persian_to_datetime(customer['date_time_to_remember']))
        customer['sortable_date'] = persian_to_datetime(customer['date_time_to_remember'])
    sorted_data = sorted(serializer_data, key=lambda x: x['sortable_date'] or datetime.max)

    for customer in serializer_data:
        del customer['sortable_date']
    return Response(status=status.HTTP_200_OK, data={
        "status": True,
        "message": "موفق",
        "data": {
            "count": paginator.count,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": sorted_data
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def create_label_steps(request):
    steps = [
        {
            "title": "مرحله 1",
            "step": 1,
        },
        {
            "title": "مرحله 2",
            "step": 2,
        },
        {
            "title": "مرحله 3",
            "step": 3,
        },
        {
            "title": "مرحله 3",
            "step": 3,
        },
        {
            "title": "مرحله 4",
            "step": 4,
        },
        {
            "title": "مرحله 5",
            "step": 5,
        },
    ]
    for label in Label.objects.all():



        new_label_step = LabelStep.objects.create(label=label)
        for step in steps:
            new_step = Step.objects.create(
                    title=step['title'],
                    step=step['step'],
                    label_step=new_label_step
            )
    return Response(status=status.HTTP_200_OK)


class LabelStepManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request):
        label_id = request.GET.get("label_id")
        label_obj = get_object_or_404(Label,id=label_id)
        step_objs =label_obj.label_step.steps.all()
        serializer_data = LabelStepSerializer(step_objs,many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":serializer_data.data
        })
    def put(self,request,step_id):
        step_obj = get_object_or_404(Step,id=step_id)
        serializer_data = LabelStepSerializer(data=request.data,instance=step_obj)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت به روزرسانی شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "error",
            "data": serializer_data.errors
        })
    def post(self,request):
        serializer_data = LabelStepSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED, data={
                "status": True,
                "message": "با موفقیت به ثبت شد",
                "data": serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "errror",
            "data": serializer_data.errors
        })



    def delete(self,request,step_id):
        order_step = request.data.get("order_step",[])
        step_obj_deleted = get_object_or_404(Step,id=step_id)
        step_obj_deleted.delete()
        for order in order_step :
            step_obj = Step.objects.get(id=order['id'])
            step_obj.step = order['step']
            step_obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)




def get_customers_by_role(user, workspace,group_crm_obj):
    if workspace.owner == user:
        return CustomerUser.objects.filter(is_followed=True,group_crm=group_crm_obj)

    workspace_member = get_object_or_404(WorkspaceMember, user_account=user, workspace=workspace)

    for permission in workspace_member.permissions.all():
        if permission.permission_name == "crm" and permission.permission_type == "manager":
            return CustomerUser.objects.filter(is_followed=True,group_crm=group_crm_obj)

    return CustomerUser.objects.filter(is_followed=True, user_account=user,group_crm=group_crm_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def customer_success_sells(request):

    page_number = request.GET.get("page_number", 1)
    group_crm_id = request.GET.get("group_crm_id")
    group_crm_obj = get_object_or_404(GroupCrm, id=group_crm_id)
    workspace_obj = get_object_or_404(WorkSpace, id=request.user.current_workspace_id)

    customer_objs = get_customers_by_role(request.user, workspace_obj,group_crm_obj)
    pagination_data = pagination(query_set=customer_objs, page_number=page_number)

    if pagination_data['list']:
        pagination_data['list'] = CustomerSmallSerializer(pagination_data['list'], many=True).data

    return Response(
        status=status.HTTP_200_OK,
        data={"status": True, "message": "موفق", "data": pagination_data}
    )


class CustomerDocumentManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,document_id=None):
        if document_id:
            document_obj =get_object_or_404(CustomerDocument,id=document_id)
            serializer_data = CustomerDocumentSerializer(document_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        group_crm_id= request.GET.get("group_crm_id")
        group_crm_obj  = get_object_or_404(GroupCrm,id=group_crm_id)
        document_objs =CustomerDocument.objects.filter(group_crm=group_crm_obj)
        serializer_data = CustomerDocumentSerializer(document_objs,many=True)
        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "موفق",
            "data": serializer_data.data
        })
    def post (self,request):
        serializer_data = CustomerDocumentSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت آپلود شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.errors
        })
    def delete(self,request,document_id):
        document_obj = get_object_or_404(CustomerDocument,id=document_id)
        document_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerBankManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]
    def get(self,request,customer_b_id=None):
        page_number =request.GET.get("page_number",1)
        if customer_b_id:
            customer_bank_obj =get_object_or_404(CustomerBank,id=customer_b_id)
            serializer_data = CustomerBankSerializer(customer_bank_obj)

            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        document_id =request.GET.get("document_id")
        document_obj= get_object_or_404(CustomerDocument,id=document_id)
        customer_bank_objs = CustomerBank.objects.filter(document=document_obj)
        paginate_data = pagination(page_number=page_number,query_set=customer_bank_objs)
        paginate_data['list'] = CustomerBankSerializer(paginate_data['list'],many=True).data


        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "موفق",
            "data": paginate_data
        })
    def post(self,request):
        serializer_data = CustomerBankSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت ثبت",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "Validation Error",
            "data": serializer_data.errors
        })
    def put(self,request,customer_b_id):
        customer_bank = get_object_or_404(CustomerBank,id=customer_b_id)

        serializer_data = CustomerBankSerializer(data=request.data,instance=customer_bank)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "status": False,
            "message": "Validation Error",
            "data": serializer_data.errors
        })
    def delete(self,request,customer_b_id):
        customer_bank = get_object_or_404(CustomerBank, id=customer_b_id)
        customer_bank.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
@api_view(['POST'])
def send_a_customer_to_board(request):
    customer_bank_id_list = request.data.get("customer_bank_id_list")
    group_crm_id = request.data.get("group_crm_id")
    for customer_b_id in customer_bank_id_list:
        customer_bank_obj = get_object_or_404(CustomerBank,id=customer_b_id)
        first_label = Label.objects.filter(group_crm_id=group_crm_id).last()



        state = None
        city=  None
        if customer_bank_obj.is_local:
            if customer_bank_obj.state:
                if State.objects.filter(name=customer_bank_obj.state).exists():
                    state = State.objects.filter(name=customer_bank_obj.state).first()
            if customer_bank_obj.city:
                if City.objects.filter(name=customer_bank_obj.city).exists():
                    city = City.objects.filter(name=customer_bank_obj.city).first()
        else:
            state = customer_bank_obj.main_state
            city = customer_bank_obj.main_city
        new_customer = CustomerUser.objects.create(
            group_crm_id=group_crm_id,
            fullname_or_company_name = customer_bank_obj.fullname_or_company_name,
            phone_number= customer_bank_obj.phone_number,
            phone_number_static = customer_bank_obj.static_phone_number ,
            city = city ,
            user_account=request.user,
            state = state ,
            address = customer_bank_obj.address ,
            email = customer_bank_obj.email ,
            label=first_label,
        )
        customer_bank_obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



class CustomerStatusManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceMemberAccess]

    def post(self,request,customer_id):

        request.data['customer_id'] = customer_id
        serializer_data = CustomerStatusSerializer(data=request.data,context={"user":request.user})
        request.data['workspace_id'] = request.user.current_workspace_id
        if serializer_data.is_valid():
            customer_obj = serializer_data.save()
            response_data = CustomerSmallSerializer(customer_obj).data
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"با موفقیت ثبت شد",
                "data":response_data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"Validation Error",
            "data":serializer_data.errors
        })




@api_view(['POST'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def resell_a_customer(request,customer_id):
    customer_obj = get_object_or_404(CustomerUser,id=customer_id)

    last_label = Label.objects.filter(group_crm=customer_obj.group_crm).last()
    last_customer_in_label = CustomerUser.objects.filter(label=last_label).order_by("order").last()
    if last_customer_in_label:
        customer_obj.order = last_customer_in_label.order +1
    customer_obj.label = last_label
    customer_obj.is_followed = False
    customer_obj.save()
    channel_layer = get_channel_layer()

    event = {
            'type': 'send_customer_list',
            "group_crm_id": customer_obj.group_crm.id
        }

    async_to_sync(channel_layer.group_send)(f"{customer_obj.group_crm.id}_gp_group_crm", event)
    serializer_data = CustomerSmallSerializer(customer_obj)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"با موفقیت ارسال شد",
        "data":serializer_data.data
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated,IsWorkSpaceMemberAccess])
def change_customer_step(request,customer_id):
    data = request.data
    step = int(data['step'])
    customer_obj = CustomerUser.objects.get(id=customer_id)
    step_obj = None
    for step_item in customer_obj.label.label_step.steps.all():
        if step_item.step == step:
            step_obj = step_item

    new_step_customer = CustomerStep.objects.create(
        customer=customer_obj,
        label=customer_obj.label,
        step=step_obj
    )
    channel_layer = get_channel_layer()

    event = {
            'type': 'send_customer_list',
            "group_crm_id": customer_obj.group_crm.id
        }

    async_to_sync(channel_layer.group_send)(f"{customer_obj.group_crm.id}_gp_group_crm", event)
    serializer_data = CustomerSmallSerializer(customer_obj)
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"با موفقیت انجام شد",
        "data":serializer_data.data
    })