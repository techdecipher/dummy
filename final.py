import json
import boto3
from datetime import datetime

ses_client = boto3.client('ses')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))
    pipeline_name = event['detail']['pipeline']
    state = event['detail']['state']
    execution_id = event['detail']['execution-id']
    region = event['region']
    account_id = event['account']
    time = event['time']
    
    dt = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z")
    Failure_time = dt.strftime("%Y-%m-%d %H:%M:%S")

    subject = f'CodePipeline Failure Notification: {pipeline_name}'
    body = f"""
    Hello Team,

    This is to notify you that the below CI-CD Pipeline has failed.

    Details:
    - Pipeline Name: {pipeline_name}
    - State: {state}
    - Execution ID: {execution_id}
    - Region: {region}
    - Time: {Failure_time}

    Please take the necessary actions to investigate and resolve the issue.

    Best regards,
    Your DevOps Team
    """

    response = ses_client.send_email(
        Source='pranav.chaudhari@ge.com', 
        Destination={
            'ToAddresses': ['user1@gem.com',
            'user2@gem.com',
            'user3@gem.com']
        },
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
    return response
