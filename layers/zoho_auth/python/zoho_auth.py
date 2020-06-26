import requests
import json
import boto3

# Initially, a self-client and web client will need to be created, even if the web client has a dummy redirect_uri
# value. Gather the below information and input into secretsmanager as json plaintext:
# {
#   "client_id": "From self-client",
#   "client_secret": "From self-client,
#   "redirect_uri": "from web client",
#   "code": "authorization code/grant token that is generated from self-client (scope to use is below)",
#   "org_id": "from zoho desk API settings page"
# }

# Scope to input for generation of the authorization code. All separated by commas, no spaces (all access):
# Desk.tickets.ALL,Desk.tasks.ALL,Desk.settings.ALL,Desk.search.READ,Desk.events.ALL,Desk.articles.READ,
# Desk.articles.CREATE,Desk.articles.UPDATE,Desk.articles.DELETE,Desk.contacts.READ,Desk.contacts.WRITE,
# Desk.contacts.UPDATE,Desk.contacts.CREATE,Desk.basic.READ,Desk.basic.CREATE,Aaaserver.profile.ALL

# Areas for improvement: needs to return better error messages and invalid_code (expired authorization code) error
# message instead of KeyError.


def call_api(secret_id, path):
    try:
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(
            SecretId=secret_id
        )
        secret = eval(response['SecretString'])
        client_id = secret['client_id']
        client_secret = secret['client_secret']
        redirect_uri = secret['redirect_uri']
        code = secret['code']
        org_id = secret['org_id']

        if 'access_token' in secret:
            access_token = secret['access_token']
            refresh_token = secret['refresh_token']
            try:
                headers = {'orgId': org_id, 'Authorization': f'Zoho-oauthtoken {access_token}'}
                call_api_route = requests.get(f'https://desk.zoho.com/api/v1/{path}', headers=headers)
                payload = call_api_route.text
                print(payload)
                if 'errorCode' in payload:
                    if payload['errorCode'] == "INVALID_OAUTH":
                        refresh_access_token_params = {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "refresh_token": refresh_token,
                            "grant_type": "refresh_token"
                        }
                        refresh_access_token = requests.post('https://accounts.zoho.com/oauth/v2/token',
                                                             params=refresh_access_token_params)
                        refresh_access_token_content = json.loads(refresh_access_token.text)
                        access_token = refresh_access_token_content['access_token']
                        headers = {'orgId': org_id, 'Authorization': f'Zoho-oauthtoken {access_token}'}
                        call_api_route = requests.get(f'https://desk.zoho.com/api/v1/{path}', headers=headers)
                        payload = call_api_route.json()

                    return {
                        'statusCode': 200,
                        'body': json.loads(payload)
                    }

                else:
                    return {
                        'statusCode': 200,
                        'body': json.loads(payload)
                    }

            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': str(e)
                }

        else:
            access_token_params = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "access_type": "offline",
                "prompt": "consent"
            }
            get_access_token = requests.post('https://accounts.zoho.com/oauth/v2/token', params=access_token_params)
            get_access_token_content = json.loads(get_access_token.text)
            secret['access_token'] = get_access_token_content['access_token']
            secret['refresh_token'] = get_access_token_content['refresh_token']
            client.put_secret_value(
                SecretId=secret_id,
                SecretString=f'{secret}'
            )
            try:
                headers = {'orgId': org_id, 'Authorization': f'Zoho-oauthtoken {access_token}'}
                call_api_route = requests.get(f'https://desk.zoho.com/api/v1/{path}', headers=headers)
                payload = call_api_route.text

                return {
                    'statusCode': 200,
                    'body': json.loads(payload)
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': str(e)
                }
    except Exception as e:
        return e


# if get_access_token_content['error'] == 'invalid_code':
#     return 'Please generate a new grant token (code) and save it in the secret. Then try again.'
# else: