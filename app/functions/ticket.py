import zoho_auth


def list_tickets(event, context):
    secret_id = event['secret_id']
    path = event['path']
    try:
        return zoho_auth.call_api(secret_id, path)

    except Exception as e:
        return str(e)