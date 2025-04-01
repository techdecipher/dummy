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

    pipeline_url = (f"https://us-east-1.console.aws.amazon.com/codesuite/codepipeline/pipelines/"
                    f"{pipeline_name}/view?action=Build-Artifacts&region=us-east-1&stage=Build_Deploy&tab=stage")

    subject = f'Dev Environment | CI/CD Pipeline Failure: {pipeline_name}'
    body = f"""
        <html>
        <body>
            <p>Hello Team,</p>
            <p>The following CI/CD pipeline has failed:</p>
            <ul>
                <li><b>Pipeline Name:</b> {pipeline_name}</li>
                <li><b>State:</b> {state}</li>
                <li><b>Execution ID:</b> {execution_id}</li>
                <li><b>Region: </b>{region}</li>
                <li><b>Time:</b>{Failure_time}</li>
                <li><b>Pipeline Logs:</b> <a href="{pipeline_url}"> Pipeline Logs </a> </li>
            </ul>
            <p>Please review the pipeline logs, investigate the root cause, and take necessary actions to resolve the issue.</p>
            <p><b>Best regards,</b><br>DevOps Team</p>
        </body>
        </html>
    """

    response = ses_client.send_email(
        Source='user@testdomain.com',  # Replace with your verified SES email address
        Destination={
            'ToAddresses': ['pranav.chaudhari@testdomain.com']  # Replace with the recipient's email address
        },
        Message={
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': body, 'Charset': 'UTF-8'}}
        }
    )
    return response
