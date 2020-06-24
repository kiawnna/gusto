import requests
import json
# import zcrmsdk
# from zcrmsdk import ZCRMModule, ZCRMException, ZohoOAuth, ZCRMRecord
import os

# Get all of this from self client except redirect_uri.
client_id = '1000.GBRO5D4O2W0L7IA99S1PIQ3D7AUWSH'
client_secret = "f1b846a3964d048af83aa86c2f98fad7e3d80c18ec"
redirect_uri = "https://www.kiastests.com/"
scope = 'Desks.tickets.READ'


def authenticate(event, context):
    get_access_token_params = {
        "code": "1000.31d0c9231efeadd40aa1107e1761fcc6.9b6fc5b8bf19b59eda2cbf1abb6777a6",
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "prompt": "consent"
    }

    response = requests.post('https://accounts.zoho.com/oauth/v2/token', params=get_access_token_params)
    refresh_token = response['refresh_token']

    refresh_access_token_params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "redirect_uri": redirect_uri,
        "scope": scope
    }

    response2 = requests.post('https://accounts.zoho.com/oauth/v2/token', params=refresh_access_token_params)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

# Response above returned this when inputing directly into POSTMAN:
# {
#     "access_token": "1000.0103918fe7c09ef865f733e75d1292d4.9451761bbc2ea300490ae447e02b55b1",
#     "refresh_token": "1000.c40d17cfb15bf5bab95ee3f62bdafd8f.fb5911c4b81e3f892bb90c90b6f2a3b6",
#     "api_domain": "https://www.zohoapis.com",
#     "token_type": "Bearer",
#     "expires_in": 3600
# }

# WITHOUT LAMBDA--JUST RUNNING IN TERMINAL
# 1. Create an App client
# 2. Create a self client
# 3. Enter in scope to self client and generate a grant token to use with the information from your app client.
# 4. Scope = AAAserver.profile.read,ZohoCRM.Modules.ALL,ZohoCRM.Bulk.READ
# 5. User grant token to generate an authtoken--this is a file that you can't open. You pass it in to your other files.
