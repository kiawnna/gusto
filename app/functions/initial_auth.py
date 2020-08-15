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


def main(event, context):
    client = boto3.client('secretsmanager')
    body = json.loads(event['body'])
    secret_id = body['secret_id']
    try:
        response = client.get_secret_value(
            SecretId=secret_id
        )
        secret = eval(response['SecretString'])
        client_id = secret['client_id']
        redirect_uri = secret['redirect_uri']
        url = 'https://api.gusto-demo.com/oauth/authorize'
        authorize_params = {
            'client_id': f'{client_id}',
            'response_type': 'code',
            'redirect_uri': f'{redirect_uri}'
        }
        response = requests.get(url=url, params=authorize_params)
        auth_url = response.url
        print(auth_url)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f'Please login via the following url to continue the authentication process. After '
                           f'logging in and granting access, you will need to save the code that appears in'
                           f'the url of the next page. {auth_url}'
            })
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
