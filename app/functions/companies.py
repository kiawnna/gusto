from app import gusto_auth
import json

# TODO: Store company info in S3.
# TODO: Fix the response. It looks funny. Or just upload to S3 and return a message.


def main(event, context):
    try:
        # body = event['body']
        body = json.loads(event['body'])
        secret_id = body['secret_id']
        path = 'companies'
        # if 'company_id' in body:
        #     path = f'companies/{body["company_id"]}'
        # else:
        #     path = 'companies'
        # #
        response = gusto_auth.main(secret_id, path)
        # json.loads(response)
        print(response)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 503,
            'body': json.dumps(str(e))
        }