import json
import boto3

ses = boto3.client('ses')

SENDER = "your-email@example.com"  # Replace with your verified SES email
RECIPIENTS = [
    "recipient1@example.com",
    "recipient2@example.com",
    "recipient3@example.com"
]  # Add more as needed

SUBJECT = "CodePipeline Failure Alert"

def lambda_handler(event, context):
    print("Received Event:", json.dumps(event, indent=4))  # Debugging: Print event details

    try:
        pipeline_name = event['detail']['pipeline']
        region = event['region']
        failure_time = event['time']
        state = event['detail']['state']

        message_body = (
            f"Hi Team,\n\n"
            f"Pipeline Name: {pipeline_name} in Region: {region} has failed at {failure_time}.\n"
            f"Its current state is: {state}.\n\n"
            f"Please check the pipeline for more details and to know the reason for failure.\n\n"
            f"Best Regards,\n"
            f"DevOps Team"
        )

        response = ses.send_email(
            Source=SENDER,
            Destination={'ToAddresses': RECIPIENTS},
            Message={
                'Subject': {'Data': SUBJECT},
                'Body': {'Text': {'Data': message_body}}
            }
        )

        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        print("Error sending email:", str(e))
    return {"statusCode": 200, "body": json.dumps("Lambda executed successfully")}
