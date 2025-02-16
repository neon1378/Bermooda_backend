from django.shortcuts import render
from rest_framework.permissions import AllowAny,IsAuthenticated,DjangoModelPermissions
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .serializers import *
from rest_framework import status
from core.permission import IsWorkSpaceMemberAccess
from WorkSpaceManager.models import WorkSpace,WorkspaceMember
from UserManager.models import UserAccount
from rest_framework.permissions import BasePermission
# Create your views here.
from core.permission import IsAccess
from dotenv import load_dotenv
import os
from django.db import transaction
load_dotenv()


class CrmDepartmentManager(APIView):
    permission_classes=[IsAuthenticated]
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
        if workspace_obj.owner == request.user:
            department_objs= CrmDepartment.objects.filter(workspace=workspace_obj)
            serializer_data = CrmDepartmentSerializer(department_objs,many=True)

        else:

            department_list = CrmDepartment.objects.filter(workspace=workspace_obj)
            department_objs = set()

            for department in department_list:
                if request.user == department.manager:
                    department_objs.add(department)
                else:
                    for project in department.project_department.all():
                        if request.user in project.members.all():
                            department_objs.add(department)
                            break
                
            department_objs=list(department_objs)
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
    permission_classes=[IsAuthenticated]
    def get(self,request,category_id=None):
        if category_id:
            category_obj = get_object_or_404(Category,id=category_id)
            serializer_data = CategorySerializer(category_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":serializer_data.data
            })
        workspace_id = request.GET.get("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        category_objs = Category.objects.filter(workspace=workspace_obj)
        serializer_data = CategorySerializer(category_objs,many=True)

        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"موفق",
            "data":serializer_data.data
        })
    def post (self,request):
        workspace_id = request.data.pop('workspace_id')
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)

        serializer_data =CategorySerializer(data=request.data)
        if serializer_data.is_valid():
            category_obj = serializer_data.create(validated_data=request.data)
            category_obj.workspace= workspace_obj
            category_obj.save()
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
    def put(self,request,category_id):
        data= request.data
        category_obj = get_object_or_404(Category,id=category_id)

        category_obj.title = data['title']
        category_obj.save()
        serializer_data = CategorySerializer(category_obj)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت بروزرسانی شد",
            "data":serializer_data.data
        })
    def delete(self,request,category_id):
        category_obj = get_object_or_404(Category,id=category_id)
        category_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class LabelMangaer(APIView):
    permission_classes=[IsAuthenticated]

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
        group_crm_id =request.data.pop("group_crm_id")
        # request.data.pop("order",None)
        group_obj = get_object_or_404(GroupCrm,id=group_crm_id)
        request.data.pop("workspace_id",None)
        serializer_data =LabelSerializer(data=request.data)
        if serializer_data.is_valid():
            label_obj = serializer_data.create(validated_data=request.data)
            label_obj.group_crm= group_obj
            label_obj.save()
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
        workspace_id = data.pop("workspace_id")
        label_obj.title = data['title']
        label_obj.color = data['color']

        label_obj.save()
        serializer_data = LabelSerializer(label_obj)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"با موفقیت بروزرسانی شد",
            "data":serializer_data.data
        })
    def delete(self,request,label_id):
        label_obj = get_object_or_404(Label,id=label_id)
        label_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class CustomerUserManager(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, customer_id=None):
        group_id = request.GET.get("group_id")
        workspace_id = request.GET.get("workspace_id")
        label_id = request.GET.get("label_id", None)

        group_obj = get_object_or_404(GroupCrm, id=group_id)
        workspace_obj = get_object_or_404(WorkSpace, id=workspace_id)

        # Handle single customer case
        if customer_id:
            customer_obj = get_object_or_404(CustomerUser, id=customer_id)
            serializer_data = CustomerSerializer(customer_obj).data
            try:
                serializer_data['label']={
                    "title":customer_obj.label.title,
                    "id":customer_obj.label.id,
                    "color":customer_obj.label.color
                }
            except:
                serializer_data['label']={}
            # Add group members 
            serializer_data['users'] = [
                {
                    "id": member.id,
                    "fullname": member.full_name(),
                    "selected": customer_obj.user_account == member,
                }
                for member in group_obj.members.all()
            ]
            return Response(
                status=status.HTTP_200_OK,
                data={"status": True, "message": "موفق", "data": serializer_data},
            )

        # Retrieve customers based on label or group
        if request.user == workspace_obj.owner:
            if label_id:
                label_obj = get_object_or_404(Label, id=label_id)
                customers = label_obj.customer_label.all()
            else:
                customers = group_obj.customer_group.all()
        else:
            if label_id:
                label_obj = get_object_or_404(Label, id=label_id)
                customers = [
                    customer
                    for customer in label_obj.customer_label.all()
                    if customer.user_account == request.user
                ]
            else:
                customers = CustomerUser.objects.filter(user_account=request.user)

        # Serialize customers
        serializer_data = CustomerSerializer(customers, many=True).data
        for item in serializer_data:
            customer_obj = CustomerUser.objects.get(id=item['id'])
            try:
                item['label']={
                    "title":customer_obj.label.title,
                    "id":customer_obj.label.id,
                    "color":customer_obj.label.color
                }
            except:
                item['label']={}
        return Response(
            status=status.HTTP_200_OK,
            data={"status": True, "message": "موفق", "data": serializer_data},
        )

    def post (self,request):
        data= request.data

        workspace_id = data.pop("workspace_id")

        group_obj =get_object_or_404(GroupCrm,id=data.pop("group_id",None))

        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        serializer_data = CustomerSerializer(data=request.data)
        if serializer_data.is_valid():
            new_customer_obj = CustomerSerializer.create(validated_data=request.data)
            new_customer_obj.user_account_id=request.user.id
            new_customer_obj.save()
            main_serializer_data = CustomerSerializer(new_customer_obj)
            new_customer_obj.workspace =workspace_obj
            new_customer_obj.group_crm =group_obj
            new_customer_obj.save()
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"موفق",
                "data":main_serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer_data.errors)
        
    def put (self,request,customer_id):
        data= request.data

        customer_obj = get_object_or_404(CustomerUser,id=customer_id)
        category =data.get("category",None)

      
        serializer = CustomerSerializer(customer_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()

            if category or category!={}:
                customer_obj.category = get_object_or_404(Category, id=category['id'])

            customer_obj.save()
            
          
            return Response( status=status.HTTP_200_OK,data={
                "status":True,
                "message":"با موفقیت بروزرسانی شد",
                "data":{}
            })
        return Response(data={
            "status":False,
            "data":serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,customer_id):
        customer_obj = get_object_or_404(CustomerUser,id=customer_id)
        customer_obj.delete()
        return Response (status=status.HTTP_204_NO_CONTENT)


class ReportManager(APIView):

    permission_classes = [IsAuthenticated]
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

    def get(self, request, group_id=None):

        workspace_id = request.GET.get("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace, id=workspace_id)

        # Fetch single group if `group_id` is provided
        if group_id:
            group_obj = get_object_or_404(GroupCrm, id=group_id)
            if request.user == workspace_obj.owner or request.user in group_obj.members.all():


                group_data = self.serialize_group(group_obj,workspace_obj)
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
            group_objs = GroupCrm.objects.filter(workspace=workspace_obj,department_id=department_id)
        else:
            if request.user_permission_type == "manager":
                group_objs = GroupCrm.objects.filter(workspace=workspace_obj,department_id=department_id)
            else:
                group_list = GroupCrm.objects.filter(workspace=workspace_obj,department_id=department_id)
                group_objs = []
                for group in group_list:
                    if request.user in group.members.all():
                        group_objs.append(group)
                

        group_data = [self.serialize_group(group,workspace_obj) for group in group_objs]
        return Response(
            status=status.HTTP_200_OK,
            data={
                "status": True,
                "message": "success",
                "data": group_data,
            },
        )

    def post(self, request):
        data = request.data
        workspace_id = data.get("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace, id=workspace_id)
        members = data.get("members", [])
        title = data.get("title")
    
        department_id = data.get("department_id",None)

        avatar_id = data.get("avatar_id",None)
        print(members)
        # Create new group
        new_group_obj = GroupCrm.objects.create(title=title,workspace=workspace_obj)
        
        new_group_obj.department_id=department_id
        new_group_obj.manager =request.user

        # Add members to the group
        for member_id in members:
            user_account = get_object_or_404(UserAccount, id=member_id)
            new_group_obj.members.add(user_account)

        # Set avatar if provided
        if avatar_id:
            main_file_obj = get_object_or_404(MainFile, id=avatar_id)
            main_file_obj.its_blong = True
            main_file_obj.save()
            new_group_obj.avatar = main_file_obj
        

        new_group_obj.save()
        print(new_group_obj.members.all().count(),"@@@@")
        label_list = [
            {
                "title":"سرنخ ها",
                "color_code":"#E726A0"
                
            },
            {
                "title":"فرصت ها",
                "color_code":"#E7C726"
            },

            {
                "title":"مشتری",
                "color_code":"#E61D1D"
            },

            {
                "title":"فاکتور",
                "color_code":"#8E19F3"
            },
            

            {
                "title":"فروش",
                "color_code":"#1DDB16"
            },
        ]
        # order= 1
        for label in label_list:
            new_label_obj = Label(title=label['title'],color=label['color_code'],group_crm=new_group_obj)

            new_label_obj.save()
            # order +=1
        group_data = self.serialize_group(new_group_obj,workspace_obj)
        print(group_data)
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "status": True,
                "message": "success",
                "data": group_data,
            },
        )

    def serialize_group(self, group_obj,workspace_obj):
        """Helper method to serialize a GroupCrm object."""
        label_objs = Label.objects.filter(group_crm=group_obj)
        users = []
        users.append(workspace_obj.owner)
        for member in WorkspaceMember.objects.filter(workspace=workspace_obj):
            if member.user_account != workspace_obj.owner:
                if member.is_accepted:
                    users.append(member.user_account)
        label_data =[]
        base_url = os.getenv("BASE_URL")
        for label in label_objs:
            label_data.append(
                    {
                           
                            "id":label.id,
                            "title":label.title,
                            "color":label.color,
                            "count":label.customer_label.filter(group_crm=group_obj).count()
                    }
                )

        return {
            "id": group_obj.id,
            
            "department":{
                "id":group_obj.department.id,
                "title":group_obj.department.id
            },
            "title": group_obj.title,
            "avatar_url": group_obj.avatar_url(),
            "label_data":label_data,
            "profit_price":group_obj.profit_price(),
            "members": [
                {
                    "id": member.id,
                    "fullname": member.full_name(),
                    "avatar_url": member.avatar_url(),
                    "selected":member in group_obj.members.all()
                }
                for member in  users 
            ],
        }
    
    def put(self,request,group_id):
        data = request.data
        group_obj = get_object_or_404(GroupCrm,id=group_id)
        workspace_id = data.get("workspace_id")
     

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
            "data":self.serialize_group(group_obj,workspace_obj)
        })
    def delete (self,request,group_id):
        data =request.data
        group_obj = get_object_or_404(GroupCrm,id=group_id)
        group_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    




@api_view(['PUT'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
        






@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_crm_group_members(request,group_id):
    workspace_obj= get_object_or_404(WorkSpace,id=request.GET.get("workspace_id",None))
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
            workspace_member = WorkspaceMember.objects.get(workspace=workspace_obj,user_account=member)
         
            if workspace_member.is_accepted:
                member_list.append({
                    "id": member.id,
                    "fullname": member.username,
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
    permission_classes  = [IsAuthenticated]
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

        data_list = []
        for custommer_obj in custommer_objs:
            not_exsit =True
            try:
                for data in data_list:
                    if data['label_id'] == custommer_obj.label.id:
                        data['customer_list'].append(CustomerSmallSerializer(custommer_obj).data)
                        not_exsit=False
                        break
                if not_exsit:
                    data_list.append({
                        "label_id":custommer_obj.label.id,
                        "color":custommer_obj.label.color,
                        "title":custommer_obj.label.title,
                        "customer_list":[CustomerSmallSerializer(custommer_obj).data]
                    })
            except:
                pass

        label_objs = Label.objects.filter(group_crm_id=group_crm_id)
        for label in label_objs:
            not_exsit= True
            for data in data_list:
                if data['label_id'] == label.id:
                    not_exsit=False
                    break
            if not_exsit:
                data_list.append({
                    "label_id": label.id,
                    "color": label.color,
                    "title": label.title,
                    "customer_list": []
                })
        # serializer_data = CustomerSmallSerializer(custommer_objs,many=True)
        return Response(status=status.HTTP_200_OK, data={
            "status": True,
            "message": "success",
            "data": data_list
        })

    def post(self,request):
        data= request.data
        data['workspace_id'] =request.user.current_workspace_id
        data['user_account_id'] =request.user.id

        serializer_data = CustomerSmallSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
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



class CampaignManager(APIView):
    permission_classes=[IsAuthenticated]
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
@permission_classes([AllowAny])
def campaign_show (request,uuid):
    campaign = get_object_or_404(Campaign,uuid=uuid)
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
    campaign = get_object_or_404(Campaign, uuid=uuid)
    new_campaign_form =CampaignForm(campaign=campaign)
    new_campaign_form.save()
    for field in field_list:
        CampaignFormData.objects.create(
            title = field['title'],
            text = field['text'],
            campaign_form = new_campaign_form
        )

    return Response(status=status.HTTP_201_CREATED,data={
        "status":True,
        "message":"success",
        "data":{}
    })


