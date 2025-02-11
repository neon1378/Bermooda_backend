
import requests
import urllib.parse
import base64


from urllib.parse import quote
def send_invite_link (phone_number,workspace_owner,workspace_name):
    try:
        convert_url = "https://server.jadoo.app/api/v1/user/auth/convertText"
        
        name = workspace_name.replace(" ","\u205f")
        
        message = workspace_owner.replace(" ","\u205f")
        # payload = {
        #     "title1":name,
        #     "title2":message
        # }
        # habib_response =requests.post(url=convert_url,data=payload)
        # print(habib_response.json())



        api_key ="6865587A4B6D694F2F39556156724B53674F386142593074583545495859734C52414A4B46384C336543383D"
        print(api_key,"@@@@")
        url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json?token={name}&token2={message}&receptor={phone_number}&template=invitelink"

        response = requests.get(url=url)
        print(response.json())

    except:
        pass

send_invite_link("09388148998","جادو","امین اله قلی")

# def sms_text(text):
#     return text.replace(' ', '\u2060')

# # مثال استفاده
# message = "سلام دنیا"
# print(sms_text(message))


# import requests

# class HttpException(Exception):
#     pass

# class ApiException(Exception):
#     pass

# def execute(url, data=None):
#     headers = {
#         'Accept': 'application/json',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'charset': 'utf-8'
#     }
    
#     try:
#         response = requests.post(url, data=data, headers=headers, verify=False)
#         code = response.status_code
#         content_type = response.headers.get('Content-Type', '')
        
#         if response.status_code != 200:
#             raise HttpException("Request have errors", code)

#         json_response = response.json()
        
#         if 'return' not in json_response or json_response['return'].get('status') != 200:
#             raise ApiException(json_response['return'].get('message', "Unknown error"), json_response['return'].get('status', code))
        
#         return json_response.get('entries')

#     except requests.exceptions.RequestException as e:
#         raise HttpException(str(e))

# مثال استفاده
# result = execute("https://example.com/api", {"key": "value"})
# print(result)