import json
import zoho_auth
import boto3
from datetime import datetime
import os

BUCKET = os.environ['BUCKET']


def main(event, context):
    s3 = boto3.client('s3')
    body = json.loads(event['body'])
    secret_id = body['secret_id']
    print(secret_id)
    company_id = body['company_id']
    path = f'companies/{company_id}/payrolls'
    try:
        response = zoho_auth.main(secret_id, path)
        body = response['body']
        payload = json.loads(body)
        all_payrolls = payload[0]
        all_payrolls = dict(all_payrolls)
        all_payrolls['name'] = 'all_payrolls_information'
        employee_comps = {k: v for (k, v) in all_payrolls.items() if 'employee_compensations' in k}
        employee_comps['name'] = 'employee_compensation_information'
        keys = {'totals', "version", "payroll_deadline", "check_date", "processed", "payroll_id", "pay_period"}
        payroll_details = {k: v for (k, v) in all_payrolls.items() if k in keys}
        payroll_details['name'] = 'other_payroll_details'
        now = datetime.now().strftime("%Y/%m/%d/%H:%M:%S")
        all_objects = [employee_comps, all_payrolls, payroll_details]
        for x in all_objects:
            print(x)
            name = x['name']
            s3.put_object(
                Body=json.dumps(x),
                Bucket=BUCKET,
                Key=f'{name}/{now}.json'
            )
        return {
            'statusCode': 200,
            'body': f'Your json files have been uploaded to bucket.'
        }
    except Exception as e:
        return e
    #
    # all_payrolls = payload[0]
    #

    # Use below to return the dictionaries in payload via postman.
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps({
    #         'employee_compensations': employee_comps,
    #         # 'other_payroll_details': list(payroll_details),
    #         'all_payrolls': all_payrolls
    #     })
    # }

# except Exception as e:
# return {
#     'statusCode': 503,
#     'body': json.dumps(str(e))
# }
#     except Exception as e:
#         return {
#             'statusCode': 503,
#             'body': json.dumps(str(e))
#         }