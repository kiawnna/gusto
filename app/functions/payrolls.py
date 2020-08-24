from app import gusto_auth
import json
import boto3
from datetime import datetime
import os
import botocore


def main(event, context):
    bucket = os.environ['BUCKET']
    s3 = boto3.client('s3')
    body = json.loads(event['body'])
    company_id = body['company_id']
    path = f'companies/{company_id}'
    try:
        employees_call = gusto_auth.main(f'{path}/employees')
        get_employees = json.loads(employees_call['body'])

        payrolls_call = gusto_auth.main(f'{path}/payrolls')
        get_payrolls = json.loads(payrolls_call['body'])

        start_dates = []
        for payroll in get_payrolls:
            start_date = payroll['pay_period']['start_date']
            start_dates.append(start_date)
            most_recent_start_date = max(start_dates)
            if payroll['pay_period']['start_date'] == most_recent_start_date:
                most_recent_payroll = payroll

        most_recent_payroll['name'] = 'all_payroll_information'

        employee_comps = most_recent_payroll['employee_compensations']

        for employee in get_employees:
            for nemployee in employee_comps:
                if nemployee['employee_id'] == employee['id']:
                    for jobs in employee['jobs']:
                        for njob in nemployee['hourly_compensations']:
                            if njob['job_id'] == jobs['id']:
                                njob['rate'] = jobs['rate']

# TODO: REVIEW THIS FROM STACKOVERFLOW. IT REQUIRES IMPORTING ANOTHER DEPENDENCY THOUGH
#         from itertools import product
#
#         for employee, nemployee in product(get_employees, employee_comps):
#             if nemployee['employee_id'] == employee['id']:
#                 for jobs, njob in product(employee['jobs'],
#                                           nemployee['hourly_compensations']):
#                     if njob['job_id'] == jobs['id']:
#                         njob['rate'] = jobs['rate']

        now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

        s3.put_object(
            Body=json.dumps(most_recent_payroll),
            Bucket=bucket,
            Key=f'payroll-start-date-{max(start_dates)}/{now}.json'
        )
        return {
            'statusCode': 200,
            'body': json.dumps(f'Your json files have been uploaded to bucket {bucket}.')
        }

    except botocore.exceptions.ParamValidationError as error:
        raise ValueError('The parameters you provided are incorrect: {}'.format(error))
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

    # Use below to return the dictionaries in payload via postman.
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps({ most_recent_payroll })
    # }
