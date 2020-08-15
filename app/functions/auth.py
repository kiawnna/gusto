import requests
import json
import boto3

# Gather the below information and input into Secrets Manager as json plaintext:
# Put the code you received from the url after the initial authentication as "code": "your code here" into the secret in
# Secrets Manager.
# Need to test from scratch. Refreshing works.


def handle_error(e):
    # Should be a layer later.
    message = e.response['Error']['Message']
    status_code = e.response['ResponseMetadata']['HTTPStatusCode']
    return {
        "statusCode": status_code,
        "body": message
    }


def main(event, context):
    client = boto3.client('secretsmanager')
    body = json.loads(event['body'])
    path = body['path']
    try:
        # will get secret_id from functions that need to authenticate with this layer. currently hard-coded
        response = client.get_secret_value(
            SecretId='gusto_auth'
        )
        secret = eval(response['SecretString'])

        if 'access_token' in secret:
            try:
                headers = {'Authorization': f'Bearer {secret["access_token"]}'}
                call_api_route = requests.get(f'https://api.gusto-demo.com/v1/{path}', headers=headers)
                header_string = str(call_api_route.headers)

                if 'invalid_token' in header_string:
                    refresh_access_token_params = {
                        "client_id": secret['client_id'],
                        "client_secret": secret['client_secret'],
                        "redirect_uri": secret['redirect_uri'],
                        "refresh_token": secret['refresh_token'],
                        "grant_type": "refresh_token"
                    }
                    refresh_access_token = requests.post('https://api.gusto-demo.com/oauth/token',
                                                         params=refresh_access_token_params).json()
                    secret['access_token'] = refresh_access_token['access_token']
                    secret['refresh_token'] = refresh_access_token['refresh_token']
                    client.put_secret_value(
                        SecretId='gusto_auth',
                        SecretString=f'{secret}'
                    )
                    headers = {'Authorization': f'Bearer {secret["access_token"]}'}
                    payload = requests.get(f'https://api.gusto-demo.com/v1/{path}', headers=headers).json()

                    return {
                        'statusCode': 200,
                        'body': json.dumps(payload)
                    }

                else:
                    payload = call_api_route.json()
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
                'client_id': secret['client_id'],
                'client_secret': secret['client_secret'],
                'code': secret['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': secret['redirect_uri']
            }
            url = 'https://api.gusto-demo.com/oauth/token'

            get_access_token = requests.post(url=url, params=access_token_params).json()
            if 'error' in get_access_token:
                if get_access_token['error'] == "invalid_grant":
                    return {
                        'statusCode': 400,
                        'body': get_access_token
                    }
            else:
                secret['access_token'] = get_access_token['access_token']
                secret['refresh_token'] = get_access_token['refresh_token']
                client.put_secret_value(
                    SecretId='gusto_auth',
                    SecretString=f'{secret}'
                )
                try:
                    headers = {'Authorization': f'Bearer {secret["access_token"]}'}
                    payload = requests.get(f'https://api.gusto-demo.com/v1/{path}', headers=headers).json()

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
