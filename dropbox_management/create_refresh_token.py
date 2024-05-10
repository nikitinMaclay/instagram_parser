import requests

app_key = "szk2ufhycz01zqh"
secret_key = "xjo2fzzr0oohm1k"
getting_code_link = "https://www.dropbox.com/oauth2/authorize?client_id=lyccpb244lywmem&response_type=code&token_access_type=offline"

url = "https://api.dropbox.com/oauth2/token"
data = {
    "code": "YOUR_CODE",
    "grant_type": "authorization_code"
}
auth = (app_key, secret_key)

response = requests.post(url, data=data, auth=auth)
print(response.json())