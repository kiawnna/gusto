import zoho_auth

# Path in the name of the secret you are pulling from and the path as an event in lambda.
# The path: "tickets" returns a list of all tickets.


def list_tickets(event, context):
    secret_id = event['secret_id']
    path = event['path']
    try:
        return zoho_auth.call_api(secret_id, path)

    except Exception as e:
        return str(e)