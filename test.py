import os
from UserManager.models import UserAccount
user_objs = UserAccount.objects.all()
import requests
for user_acc in user_objs:
    if user_acc.phone_number:
        jadoo_base_url = os.getenv("JADOO_BASE_URL")
        # send user to jadoo

        url = f"{jadoo_base_url}/user/auth/createBusinessUser"

        payload = {
            "mobile": user_acc.phone_number,
            "fullname": user_acc.fullname,
            "avatar_url": user_acc.avatar_url(),

        }
        response_data = requests.post(url=url, data=payload)
        print(response_data.json())
        recive_data = response_data.json()

        user_acc.refrence_id = int(recive_data['data']['id'])
        user_acc.refrence_token = recive_data['data']['token']
        user_acc.save()
