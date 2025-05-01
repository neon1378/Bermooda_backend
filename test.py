import os
import requests
from dotenv import load_dotenv
from UserManager.models import UserAccount
load_dotenv()



class ExternalApi:
    def __init__(self,token,headers_required=True):
        self.base_url = os.getenv("JADOO_BASE_URL")
        self.headers_required = headers_required

        self.token = token
        self.headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json',
        }
    def get(self,params=None,end_point=None):
        try:
            url = {self.base_url} + end_point
            if self.headers_required:
                response = requests.get(url=url,params=params,headers=self.headers)
            else:
                response = requests.get(url=url,params=params)

            return response.json()
        except:
            return False
    def post(self,data,end_point):
        try:
            url = {self.base_url} + end_point
            if self.headers_required:
                response = requests.post(url=url,data=data,json=data,headers=self.headers)
            else:
                response = requests.post(url=url,data=data,json=data)

            return response.json()
        except:
            return None




api_connect = ExternalApi(token="asdasd",headers_required=False)
user_acc = UserAccount.objects.get(id=80)
post_request = api_connect.post(
    data={
        "mobile": user_acc.phone_number,
        "fullname": user_acc.phone_number,
        "avatar_url": user_acc.avatar_url(),
    },
    end_point="/user/auth/createBusinessUser"
)
print(post_request)
user_acc.refrence_id = int(post_request['data']['id'])
user_acc.refrence_token = post_request['data']['token']
user_acc.save()