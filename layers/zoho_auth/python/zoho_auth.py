import requests
import json
import boto3


def handle_error(e):
    # Should be a layer later.
    message = e.response['Error']['Message']
    status_code = e.response['ResponseMetadata']['HTTPStatusCode']
    return {
        "statusCode": status_code,
        "body": message
    }
#
# def call_api(access_token, path):
#


def main(secret_id, path):
    client = boto3.client('secretsmanager')
    try:
        response = client.get_secret_value(
            SecretId=secret_id
        )
        secret = eval(response['SecretString'])
        client_id = secret['client_id']
        client_secret = secret['client_secret']
        redirect_uri = secret['redirect_uri']
        code = secret['code']

        if 'access_token' in secret:
            access_token = secret['access_token']
            refresh_token = secret['refresh_token']
            try:
                headers = {'Authorization': f'Bearer {access_token}'}
                call_api_route = requests.get(f'https://api.gusto-demo.com/v1/{path}', headers=headers)
                header_string = str(call_api_route.headers)

                if 'invalid_token' in header_string:
                    refresh_access_token_params = {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token"
                    }
                    refresh_access_token = requests.post('https://api.gusto-demo.com/oauth/token',
                                                         params=refresh_access_token_params)
                    refresh_access_token_content = json.loads(refresh_access_token.text)
                    secret['access_token'] = refresh_access_token_content['access_token']
                    secret['refresh_token'] = refresh_access_token_content['refresh_token']
                    client.put_secret_value(
                        SecretId='gusto_auth',
                        SecretString=f'{secret}'
                    )
                    access_token = secret['access_token']
                    refresh_token = secret['refresh_token']
                    headers = {'Authorization': f'Bearer {access_token}'}
                    call_api_route = requests.get(f'https://api.gusto-demo.com/v1/{path}', headers=headers)
                    payload = json.loads(call_api_route.text)

                    return {
                        'statusCode': 200,
                        'body': json.dumps(payload)
                    }

                else:
                    payload = json.loads(call_api_route.text)
                    return {
                        'statusCode': 200,
                        'body': json.dumps(payload)
                    }

            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': json.dumps(str(e))
                }

        else:
            access_token_params = {
                'client_id': f'{client_id}',
                'client_secret': f'{client_secret}',
                'code': f'{code}',
                'grant_type': 'authorization_code',
                'redirect_uri': f'{redirect_uri}'
            }
            url = 'https://api.gusto-demo.com/oauth/token'

            get_access_token = requests.post(url=url, params=access_token_params)
            get_access_token_content = json.loads(get_access_token.text)
            if 'error' in get_access_token_content:
                if get_access_token_content['error'] == "invalid_grant":
                    return {
                        'statusCode': 400,
                        'body': get_access_token_content
                    }
            else:
                secret['access_token'] = get_access_token_content['access_token']
                secret['refresh_token'] = get_access_token_content['refresh_token']
                client.put_secret_value(
                    SecretId='gusto_auth',
                    SecretString=f'{secret}'
                )
                access_token = secret['access_token']
                refresh_token = secret['refresh_token']
                try:
                    headers = {'Authorization': f'Bearer {access_token}'}
                    call_api_route = requests.get(f'https://api.gusto-demo.com/v1/{path}', headers=headers)
                    payload = call_api_route.text

                    return {
                        'statusCode': 200,
                        'body': json.loads(payload)
                    }
                except Exception as e:
                    return {
                        'statusCode': 501,
                        'body': str(e)
                    }

    except Exception as e:
        return {
            'statusCode': 501,
            'body': str(e)
        }

    except client.exceptions.ResourceNotFoundException as e:
        return handle_error(e)
    except client.exceptions.InvalidParameterException as e:
        return handle_error(e)
    except client.exceptions.InvalidRequestException as e:
        return handle_error(e)
    except client.exceptions.DecryptionFailure as e:
        return handle_error(e)
    except client.exceptions.InternalServiceError as e:
        return handle_error(e)

