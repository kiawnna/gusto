from app import gusto_auth
import json
import boto3
from datetime import datetime
import os
import botocore
BUCKET = os.environ['BUCKET']


def main(event, context):
    s3 = boto3.client('s3')
    body = json.loads(event['body'])
    company_id = body['company_id']
    path = f'companies/{company_id}/payrolls'
    try:
        response = gusto_auth.main(path)
        payload = json.loads(response['body'])
        all_payrolls = dict(payload[0])

        all_payrolls['name'] = 'all_payrolls_information'
        employee_comps = {k: v for (k, v) in all_payrolls.items() if 'employee_compensations' in k}

        employee_comps['name'] = 'employee_compensation_information'
        keys = {'totals', "version", "payroll_deadline", "check_date", "processed", "payroll_id", "pay_period"}

        payroll_details = {k: v for (k, v) in all_payrolls.items() if k in keys}
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
            'body': json.dumps(f'Your json files have been uploaded to bucket {BUCKET}.')
        }

    except botocore.exceptions.ParamValidationError as error:
        raise ValueError('The parameters you provided are incorrect: {}'.format(error))
    # except s3.exceptions.ResourceNotFoundException as e:
    #     message = e.response['Error']['Message']
    #     status_code = e.response['ResponseMetadata']['HTTPStatusCode']
    #     return {
    #         "statusCode": status_code,
    #         "body": message
    #     }
    # except Exception as e:
    #     return str(e)
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