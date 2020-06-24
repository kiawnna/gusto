import requests
import json
import boto3

# Get all of this from self client except redirect_uri.
# Initially, a self client and web client need to be created. The self client needs to be given the following scopes,
# separated by commas: . Then, a grant_token (named code below and stored as code) needs to be generated and stored in
# the secret you pass into the function.


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
                payload = call_api_route.json()

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
                    payload = call_api_route.text

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
            response_get_access_token = json.loads(get_access_token.text)
            access_token = response_get_access_token['access_token']
            refresh_token = response_get_access_token['refresh_token']
            add_tokens_to_secret = client.put_secret_value(
                SecretId=secret_id,
                SecretString=[{"access_token": access_token}, {"refresh_token": refresh_token}]
            )
            headers = {'orgId': org_id, 'Authorization': f'Zoho-oauthtoken {access_token}'}
            call_api_route = requests.get(f'https://desk.zoho.com/api/v1/{path}', headers=headers)
            payload = call_api_route.text

            return {
                'statusCode': 200,
                'body': json.loads(payload)
            }

    except Exception as e:
        return e
