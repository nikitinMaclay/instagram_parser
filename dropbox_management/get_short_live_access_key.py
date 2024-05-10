import requests


def get_access_token():

    refresh_token = "clydu3Qm-bwAAAAAAAAAARM2AIH23RLRh2qyL2W7zXBpupai8UpFJrtJuIEgoiFb"

    app_key = "szk2ufhycz01zqh"
    secret_key = "xjo2fzzr0oohm1k"

    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "refresh_token": f"{refresh_token}",
        "grant_type": "refresh_token",
        "client_id": f"{app_key}",
        "client_secret": f"{secret_key}"
    }

    response = requests.post(url, data=data).json()
    return response
