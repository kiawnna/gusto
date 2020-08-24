from app import gusto_auth
import json


def main(event, context):
    try:
        path = 'companies'
        response = gusto_auth.main(path)
        companies = response['body']
        print(companies)
        return {
            'statusCode': 200,
            'body': companies
        }
    except Exception as e:
        return {
            'statusCode': 503,
            'body': json.dumps(str(e))
        }