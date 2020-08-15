import json
import requests
import boto3
from datetime import datetime
import os

BUCKET = os.environ['BUCKET']
# Add a route to get just most current payroll.


def main(event, context):
    s3 = boto3.client('s3')
    body = json.loads(event['body'])
    company_id = body['company_id']
    access_token = 'c09794cdcdea29cbe21b4945f9e9db65983cb480ce91ad335e98c541130a0494'
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        call_api = requests.get(f'https://api.gusto-demo.com/v1/companies/{company_id}/payrolls', headers=headers).json()
        all_payrolls = call_api[0]
        all_payrolls['name'] = 'all_payrolls_information'
        employee_comps = {k:v for (k,v) in all_payrolls.items() if 'employee_compensations' in k}
        employee_comps['name'] = 'employee_compensation_information'
        keys = {'totals', "version", "payroll_deadline", "check_date", "processed", "payroll_id", "pay_period"}
        payroll_details = {k:v for (k,v) in all_payrolls.items() if k in keys}
        payroll_details['name'] = 'other_payroll_details'
        now = datetime.now().strftime("%Y/%m/%d/%H:%M:%S")
        all_objects = [employee_comps, all_payrolls, payroll_details]
        for x in all_objects:
            name = x['name']
            s3.put_object(
                Body=json.dumps(x),
                Bucket=BUCKET,
                Key=f'{name}/{now}.json'
            )

        return {
            'statusCode': 200,
            'body': f'Your json files have been uploaded to bucket {BUCKET}!'
        }
        # Use below to return the dictionaries in payload via postman.
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps({
        #         'employee_compensations': employee_comps,
        #         # 'other_payroll_details': list(payroll_details),
        #         'all_payrolls': all_payrolls
        #     })
        # }
    except Exception as e:
        return {
            'statusCode': 503,
            'body': json.dumps(str(e))
        }
