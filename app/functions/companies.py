import json
import zoho_auth


def main(event, context):
    body = json.loads(event['body'])
    secret_id = body['secret_id']
    path = 'companies'
    try:
        return zoho_auth.main(secret_id, path)

    except Exception as e:
        return {
            'statusCode': 503,
            'body': json.dumps(str(e))
        }