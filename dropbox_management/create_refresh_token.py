import requests

app_key = "lyccpb244lywmem"
secret_key = "z4oprbdkrpwga08"
getting_code_link = "https://www.dropbox.com/oauth2/authorize?client_id=lyccpb244lywmem&response_type=code&token_access_type=offline"

url = "https://api.dropbox.com/oauth2/token"
data = {
    "code": "NSI_DO-pNS8AAAAAAATUJpyUMCXN1IFafPLXhq5xe68",
    "grant_type": "authorization_code"
}
auth = (app_key, secret_key)

response = requests.post(url, data=data, auth=auth)
print(response.json())