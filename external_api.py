# import os
# import requests
# from dotenv import load_dotenv
# from UserManager.models import UserAccount
# load_dotenv()
#
#
#
# class ExternalApi:
#     def __init__(self,token,headers_required=True):
#         self.base_url = os.getenv("JADOO_BASE_URL")
#         self.headers_required = headers_required
#
#         self.token = token
#         self.headers = {
#             'Authorization': f"Bearer {self.token}",
#             'Content-Type': 'application/json',
#         }
#     def get(self,params=None,end_point=None):
#         try:
#             url = self.base_url + end_point
#             if self.headers_required:
#                 response = requests.get(url=url,params=params,headers=self.headers)
#             else:
#                 response = requests.get(url=url,params=params)
#
#             return response.json()
#         except:
#             return False
#     def post(self,data,end_point):
#
#         url = self.base_url + end_point
#         if self.headers_required:
#                 response = requests.post(url=url,data=data,json=data,headers=self.headers)
#         else:
#             response = requests.post(url=url,data=data,json=data)
#         print(response)
#         print(response.text)
#         return response.json()
#
# from WorkSpaceManager.models import WorkspaceMember
# from core.widgets import ExternalApi
# for member in WorkspaceMember.objects.all():
#
#
#
#     api_connection = ExternalApi(token=member.workspace.owner.refrence_token)
#
#     response_data = api_connection.post(
#         data={
#             "workSpaceId": member.workspace.jadoo_workspace_id,
#             "userId": member.user_account.refrence_id,
#             "businessUserId": member.user_account.id,
#             "businessMemberId": member.id,
#         },
#         end_point="/workspace/addWorkSpaceMember"
#     )
#     print(response_data)
#
#
#
# from WorkSpaceManager.models import WorkspaceMember,WorkSpace
# from core.widgets import ExternalApi
# import os
# from dotenv import load_dotenv
# load_dotenv()
# for workspace_obj in WorkSpace.objects.all():
#     if workspace_obj.jadoo_workspace_id == 0 or not workspace_obj.jadoo_workspace_id:
#         api_connection = ExternalApi(token=workspace_obj.owner.refrence_token)
#
#         payload = {
#
#             "cityId": None,
#             "stateId": None,
#             "name": workspace_obj.title,
#             "username": workspace_obj.jadoo_brand_name,
#             "workspaceId": workspace_obj.id,
#             "bio": workspace_obj.business_detail,
#             "avatar": "",
#             "industrialActivityId": None
#
#         }
#         if workspace_obj.city:
#             payload['cityId'] = workspace_obj.city.refrence_id
#
#         if workspace_obj.industrialactivity:
#             payload['industrialActivityId'] = workspace_obj.industrialactivity.refrence_id
#
#         if workspace_obj.state:
#             payload['stateId'] = workspace_obj.state.refrence_id
#
#         if workspace_obj.avatar:
#             base_url = os.getenv("BASE_URL")
#             payload['avatar'] = f"{base_url}{workspace_obj.avatar.file.url}"
#         response_data = api_connection.post(
#             data=payload,
#             end_point="/workspace/store"
#         )
#         print(response_data['id'],"@@2")
#         workspace_obj.jadoo_workspace_id = response_data['id']
#         workspace_obj.save()
#
#
#
#
# from UserManager.models import UserAccount
# from core.widgets import ExternalApi
# for user_acc in UserAccount.objects.all():
#         if not user_acc.phone_number:
#             user_acc.delete()
# for user_acc in UserAccount.objects.all():
#
#
#         api_connection = ExternalApi(token="asdasd", headers_required=False)
#
#         response_data = api_connection.post(
#             data={
#                 "mobile": user_acc.phone_number,
#                 "fullname": user_acc.fullname,
#                 "avatar_url": user_acc.avatar_url(),
#
#             },
#             end_point="/user/auth/createBusinessUser"
#         )
#
#         user_acc.refrence_id = int(response_data['id'])
#         user_acc.refrence_token = response_data['token']
#         user_acc.save()
#
