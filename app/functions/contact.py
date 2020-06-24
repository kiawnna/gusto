import json
import requests
import zoho_auth

access_token = '1000.8a934c467171ef25e4b94105abca718c.79ad58184469da806d79a30fc96db5fd'


def list_contacts(context, event):
    try:
        params = {}
        headers = {'orgId': '717779554', 'Authorization': f'Zoho-oauthtoken {access_token}'}
        response = requests.get('https://desk.zoho.com/api/v1/tickets', params=params, headers=headers)
        content = response.text
        print(content)

        return {
            'statusCode': 200,
            'body': json.loads(content)
        }

    except Exception as e:
        return{
            'statusCode': 500,
            'body': str(e)
        }
