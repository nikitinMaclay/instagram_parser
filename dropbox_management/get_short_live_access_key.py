import requests


def get_access_token():

    refresh_token = "1R5CJIHXPfYAAAAAAAAAAbX0Scz1qaxKlIUCrGvGRWYecxmp4dDIc0qig9CCY04R"

    app_key = "lyccpb244lywmem"
    secret_key = "z4oprbdkrpwga08"

    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "refresh_token": f"{refresh_token}",
        "grant_type": "refresh_token",
        "client_id": f"{app_key}",
        "client_secret": f"{secret_key}"
    }

    response = requests.post(url, data=data).json()
    return response
