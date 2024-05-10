import time

import dropbox
from get_short_live_access_key import get_access_token

access_token = get_access_token()["access_token"]

dbx = dropbox.Dropbox(access_token)

with open("../static/imgs/close.png", "rb") as f:
    data = f.read()
    dbx.files_upload(data, '/close.png')