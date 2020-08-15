import requests
import json


def main(event, context):
    try:
        body = json.loads(event['body'])
        api_token = body['api_token']
        headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "user": {
                "first_name": body['first_name'],
                "last_name": body['last_name'],
                "email": body['email']
            },
            "company": {
                "name": body['company_name']
            }
        }
        result = requests.post('https://api.gusto-demo.com/v1/provision',
                               headers=headers, data=json.dumps(payload))

        # response = json.loads(result.text)
        return {
            "statusCode": result.status_code,
            "body": result.text
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

