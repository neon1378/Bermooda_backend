from django.core.paginator import Paginator
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny 
from rest_framework.views import APIView
from UserManager.models import *
from .models import *
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view,permission_classes
# Create your views here.
from WorkSpaceManager.models import WorkSpace
from django.db.models import Q
from .serializers import *
from core.permission import IsWorkSpaceUser
from itertools import groupby
from django.db.models import DateField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from Notification.views import create_notification
class MailLabelManager(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceUser]
    def get (self,request,label_id=None):
        if label_id:
            mail_label_obj = get_object_or_404(MailLabel,id=label_id)
            serializer_data =MaliLabelSerializer(mail_label_obj)

            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        workspace_id= request.GET.get("workspace_id")
        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)
        mail_label_objs= MailLabel.objects.filter(workspace=workspace_obj)
        serializer_data =MaliLabelSerializer(mail_label_objs,many=True)

        
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data

        })
    def post(self,request):
        serializer_data = MaliLabelSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":serializer_data.errors
        })
    def put(self,request,label_id):
        mail_label_obj= get_object_or_404(MailLabel,id=label_id)
        request.data['workspace_id']= mail_label_obj.workspace.id
        serializer_data = MaliLabelSerializer(data=request.data,instance=mail_label_obj)
        if serializer_data.is_valid():
            serializer_data.save()

            return Response(status=status.HTTP_202_ACCEPTED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data

            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":serializer_data.errors
        })
    def delete (self,request,label_id):
        mail_label_obj= get_object_or_404(MailLabel,id=label_id)
        mail_label_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class MailManager(APIView):
    permission_classes = [IsAuthenticated,IsWorkSpaceUser]
    def _pagination_method (self,query_set,page_number,user):




        paginator = Paginator(query_set, 20)  # Set items per page

        # Check if the requested page exists
        if int(page_number) > paginator.num_pages:
            return {
                "count": paginator.count,
                "next": None,
                "previous": None,
                "list": []
            }

        # Get the page
        page = paginator.get_page(page_number)





        # Group messages by date
        serializer_data = MailSerializer(page.object_list, many=True)
        for data in serializer_data.data:
            mail_obj = Mail.objects.get(id=data['id'])

            try:
                favorite_obj = FavoriteMail.objects.get(user_account=user, mail=mail_obj)
                data['favorite_status'] = favorite_obj.status
            except:
                data['favorite_status'] = False

            if mail_obj.creator == user:
                data['status'] = "ارسال شده"
            else:
                data['status'] = "دریافت شده"


        return {
            "count": paginator.count,
            "next": page.next_page_number() if page.has_next() else None,
            "previous": page.previous_page_number() if page.has_previous() else None,
            "list": serializer_data.data
        }

    def get(self,request,mail_id=None):
        search_query = request.GET.get("search_query",None)
        page_number = request.GET.get("page_number",1)
        workspace_id = request.GET.get("workspace_id")
        is_favorite = request.GET.get("is_favorite",None)
        label_id = request.GET.get("label_id",None)
        start_date = request.GET.get("start_date", None)  # 1403/12/01
        end_date = request.GET.get("end_date", None)  # 1403/12/10




        workspace_obj = get_object_or_404(WorkSpace,id=workspace_id)


        if mail_id:
            mail_obj= get_object_or_404(Mail,id=mail_id)
                
            serializer_data = MailSerializer(mail_obj)
            if mail_obj.creator == request.user:
                serializer_data.data['status'] = "ارسال شده"
            else:
                serializer_data.data['status'] = "دریافت شده"



            serializer_data.data['sign_status']=False

            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        
        mail_objs = Mail.objects.filter(workspace=workspace_obj)
        mail_filtered = mail_objs.filter(
            Q(creator=request.user) | Q(recipients__user=request.user)
        ).distinct()
        if search_query:
            mail_filtered= mail_filtered.filter(
                title__icontains=search_query,
            )


        if start_date and end_date:
            start_date_gregorian = jdatetime.datetime.strptime(start_date, "%Y/%m/%d").togregorian()
            end_date_gregorian = jdatetime.datetime.strptime(end_date, "%Y/%m/%d").togregorian()
            mail_filtered = mail_filtered.filter(created__range=[start_date_gregorian, end_date_gregorian])

        if label_id:
            mail_filtered = mail_filtered.filter(label_id=label_id)
        if is_favorite:
            mail_filtered = [mail for mail in mail_filtered if mail.is_favorite(user=request.user)]

        serializer_data = self._pagination_method(query_set=mail_filtered,page_number=page_number,user=request.user)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":serializer_data
        })

    def post(self,request):

        request.data['creator_id'] = request.user.id
        
        mail_serializer= MailSerializer(data=request.data)
        if mail_serializer.is_valid():
            mail_obj = mail_serializer.save()
            for member in MailRecipient.objects.filter(mail=mail_obj):
                sub_title = f"نامه جدیدی از طرف {mail_obj.creator.fullname} دریافت کردید"
                title = "نامه اداری"
                create_notification(related_instance=mail_obj,workspace=WorkSpace.objects.get(id=request.data['workspace_id']),user=member.user,title=title,sub_title=sub_title,side_type="recive_mail")

            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":mail_serializer.data
            })
        return  Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":mail_serializer.errors
        })
    




class MailReportManager(APIView):

    permission_classes = [IsAuthenticated,IsWorkSpaceUser]
    def get (self,request,report_id=None):
        
        if report_id:
            mail_report_obj = get_object_or_404(MailReport,id=report_id)
            serializer_data = MailReportSerializer(mail_report_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        mail_id = request.GET.get("mail_id")
        mail_report_objs= MailReport.objects.filter(mail_id=mail_id).order_by("-created")
        serializer_data = MailReportSerializer(mail_report_objs,many=True)
        print(serializer_data.data)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data
        })
    def post(self,request):

        
        request.data['creator_id'] = request.user.id
        serializer_data = MailReportSerializer(data=request.data)
        if serializer_data.is_valid():

            serializer_data.save()


            

            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer_data.errors)
        




@permission_classes([IsAuthenticated,IsWorkSpaceUser])
@api_view(['PUT'])
def add_signature_to_mail (request,recipient_id):
    data= request.data
    signature_file_id = data['signature_file_id'] 
    mail_recipient = get_object_or_404(MailRecipient,id=recipient_id)
    if mail_recipient.user == request.user:
        main_file = MainFile.objects.get(id=signature_file_id)
        main_file.its_blong=True
        main_file.save()
        mail_recipient.signature_image = main_file
        mail_recipient.signature_status=True
        mail_recipient.save()
        mail_recipient.mail.create_mail_action(user_sender=request.user,user=mail_recipient.mail.creator,title="امضا کرد")
        for recipient in mail_recipient.mail.recipients.filter(recipient_type="sign"):
            if request.user != recipient.user:
                sub_title = f"نامه توسط  {request.user.fullname} با موفقیت امضا شد"
                title = "نامه اداری"
                create_notification(related_instance=recipient.mail,workspace=WorkSpace.objects.get(id=request.data['workspace_id']),user=recipient.user,title=title,sub_title=sub_title,side_type="mail_signatured")
            recipient.mail.create_mail_action(user_sender=request.user,user=recipient.user,title="امضا کرد")
        if request.user != mail_recipient.mail.creator:
                sub_title = f"نامه توسط  {request.user.fullname} با موفقیت امضا شد"
                title = "نامه اداری"
                create_notification(related_instance=mail_recipient.mail,workspace=WorkSpace.objects.get(id=request.data['workspace_id']),user=mail_recipient.mail.creator,title=title,sub_title=sub_title,side_type="mail_signatured")

        if mail_recipient.mail.sign_completed():
                sub_title = f"نامه {mail_recipient.mail.title} به صورت کامل امضا شده است"
                title = "نامه اداری"
                create_notification(related_instance=mail_recipient.mail,workspace=WorkSpace.objects.get(id=request.data['workspace_id']),user=mail_recipient.mail.creator,title=title,sub_title=sub_title,side_type="mail_signatured")
        serializer_data =MailRecipientSerializer(mail_recipient)
        return Response(status=status.HTTP_202_ACCEPTED,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data

        })
    return Response(status=status.HTTP_400_BAD_REQUEST,data={
        "status":False,
        "message":"امضا ارسال شده متعلق به شما نیست",
        "data":{}
    })
    

        

class MailStatusManager(APIView):
    permission_classes = [IsAuthenticated, IsWorkSpaceUser]

    def get(self, request, mail_id):
        mail_obj = get_object_or_404(Mail, id=mail_id)
        workspace_id = request.GET.get("workspace_id")

        mail_status = MailStatus.objects.filter(workspace_id=workspace_id)
        status_list = [
            {
                "id": status.id,
                "title": status.title,
                "selected": mail_obj.status_mail == status
            }
            for status in mail_status
        ]

        user_list = [
            {
                "id": member.user_account.id,
                "fullname": member.user_account.fullname,
                "avatar_url": member.user_account.avatar_url(),
                "selected":False
            }
            for member in WorkspaceMember.objects.filter(workspace_id=workspace_id)
            if member.user_account not in mail_obj.members.all() and member.user_account != mail_obj.creator
        ]

        serializer_data = {
            "status_list": status_list,
            "user_list": user_list
        }

        return Response(
            status=status.HTTP_200_OK,
            data={
                "status": True,
                "message": "success",
                "data": serializer_data
            }
        )

    def put(self, request, mail_id):
        mail_obj = get_object_or_404(Mail, id=mail_id)
        if request.user == mail_obj.creator:
            workspace_id = request.data.get('workspace_id')
            mail_status = MailStatus.objects.filter(workspace_id=workspace_id)

            user_id = request.data.get('user_id',None)
            status_id = request.data.get("status_id")

            
            if user_id:
                user_receiver = get_object_or_404(UserAccount,id=user_id)

                if mail_obj.creator != user_receiver:

                    mail_obj.create_mail_action(user_sender=user_receiver,user=user_receiver,title="ارجاع داده شد")
                    for member in mail_obj.members.all():
                        mail_obj.create_mail_action(user_sender=user_receiver,user=member,title="ارجاع داده شد")
                mail_obj.creator=user_receiver
                mail_obj.save()
            if status_id:
                mail_status_obj = get_object_or_404(MailStatus,id=status_id)
                if mail_status_obj != mail_obj.status_mail:
                    mail_obj.create_mail_action(user_sender=mail_obj.creator,user=mail_obj.creator,title=f"به {mail_status_obj.title} تغییر وضعیت داده شد")

                    for member in mail_obj.members.all():
                        mail_obj.create_mail_action(user_sender=mail_obj.creator,user=member,title=f"به {mail_status_obj.title} تغییر وضعیت داده شد")
                    

                mail_obj.status_mail = mail_status_obj
                mail_obj.save()
    

            status_list = [
                {
                    "id": status.id,
                    "title": status.title,
                    "selected": mail_obj.status_mail == status
                }
                for status in mail_status
            ]

            user_list = [
                {
                    "id": member.user_account.id,
                    "fullname": member.user_account.fullname,
                    "avatar_url": member.user_account.avatar_url(),
                    "selected": False,
                }
                for member in WorkspaceMember.objects.filter(workspace_id=workspace_id)
                if member.user_account not in mail_obj.members.all() and member.user_account != mail_obj.creator
            ]


            serializer_data = {
                "status_list": status_list,
                "user_list": user_list
            }

            return Response(
                status=status.HTTP_202_ACCEPTED,
                data={
                    "status": True,
                    "message": "success",
                    "data": serializer_data
                }
            )
        return Response(status=status.HTTP_403_FORBIDDEN,data={
            "status":True,
            "message":"access denaid",
            "data":{}
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def create_statuses (request):
    workspaces = WorkSpace.objects.all()
    default_statuses = [
            {
                "title":"امضا شده",
                
            },
            {
                "title":"در انتظار امضا",
                
                
            },
            {
                "title":"معلق",
                
            },

            {
                "title":"منتظر پاسخ",
                
            },
            {
                "title":"بایگانی شده",
                
            },
            {
                "title":"پیش نویس",
                
            },      
        ]
    
    for workspace in workspaces:
        for statuss in default_statuses:
            mail_status_obj = MailStatus.objects.create(title=statuss['title'],workspace=workspace)
    return Response(status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated,IsWorkSpaceUser])
def add_or_discard_to_favorite(request,mail_id):
    mail_obj = get_object_or_404(Mail,id=mail_id)
    try:
        favorite_obj = FavoriteMail.objects.get(
                mail= mail_obj,
                user_account= request.user
        
        )
    except:
        favorite_obj = FavoriteMail.objects.create(
            mail=mail_obj,
            user_account = request.user
        )
    favorite_obj.status= request.data['favorite_status']
    favorite_obj.save()
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":{}
    })
@permission_classes([IsAuthenticated,IsWorkSpaceUser])
@api_view(['GET'])
def mail_actions (request,mail_id):
    # Get the Mail object
    mail_obj = get_object_or_404(Mail, id=mail_id)

    # Filter MailAction objects related to the mail and owned by the request user
    mail_actions = MailAction.objects.filter(mail=mail_obj, owner=request.user).annotate(
        created_date=Cast('created', DateField())
    ).order_by('created_date')
    for created_date, actions in groupby(mail_actions, key=lambda x: x.created_date):
        print(type(created_date))
    # Group by `created_date`
    grouped_mail_actions = {
        jdatetime.datetime.fromgregorian(datetime=created_date).strftime("%Y/%m/%d"): [
            {
                "id": action.id,
                "title": action.title,
                
                "user":MemberSerializer(action.user_sender).data ,
                "time":jdatetime.datetime.fromgregorian(datetime=action.created).strftime("%H:%M")
            }
            for action in actions
        ]
        for created_date, actions in groupby(mail_actions, key=lambda x: x.created_date)
    }
    return Response(status=status.HTTP_200_OK,data={
        "status":True,
        "message":"success",
        "data":grouped_mail_actions
    })




class CategoryDraftManger(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceUser]
    def get(self,request,category_id=None):
        if category_id:
            category_obj  = get_object_or_404(CategoryDraft,id=category_id)
            serializer_data=CategoryDraftSerializer(category_obj)
            
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                
                "message":"success",
                "data":serializer_data.data
            })
        workspace_id = request.GET.get("workspace_id")
        
        serializer_data = CategoryDraftSerializer(CategoryDraft.objects.filter(workspace_id=workspace_id,owner=request.user),many=True)
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":serializer_data.data

        })
    def post(self,request):
      
        request.data['owner_id'] = request.user.id
        serializer_data= CategoryDraftSerializer(data=request.data)

        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":serializer_data.errors
        })
    def put(self,request,category_id):
        instance = get_object_or_404(CategoryDraft,id=category_id)
        serializer_data = CategoryDraftSerializer(instance=instance,data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data

            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":serializer_data.errors

        })



    def delete(self,request,category_id):
        instance = get_object_or_404(CategoryDraft,id=category_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DraftManger(APIView):
    permission_classes=[IsAuthenticated,IsWorkSpaceUser]
    def get(self,request,draft_id=None):
        if draft_id:
            draft_obj = get_object_or_404(DraftManger,id=draft_id)
            serializer_data = DraftSerializer(draft_obj)
            return Response(status=status.HTTP_200_OK,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data

            })

        workspace_id= request.GET.get("workspace_id")
        response_data =[]
        
        for category in CategoryDraft.objects.filter(workspace_id=request.GET.get("workspace_id"),owner= request.user):
            dic ={
            "category_id":category.id,
            "category_title":category.title,
            "color_code":category.color_code,
            "draft_data":[]
                        
            }

            for draft in Draft.objects.filter(workspace_id=workspace_id,owner=request.user):
                if draft.category == category:  
                    dic['draft_data'].append(DraftSerializer(draft).data)
            response_data.append(dic)
            
     
        return Response(status=status.HTTP_200_OK,data={
            "status":True,
            "message":"success",
            "data":response_data
        })
        

    def post(self,request):
        request.data['owner_id'] =request.user.id
        serializer_data=DraftSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":serializer_data.errors

        })
    def put(self,request,draft_id):
        draft_obj = get_object_or_404(Draft,id=draft_id)
        serializer_data = DraftSerializer(instance=draft_obj,data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(status=status.HTTP_201_CREATED,data={
                "status":True,
                "message":"success",
                "data":serializer_data.data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST,data={
            "status":False,
            "message":"error",
            "data":serializer_data.errors

        })