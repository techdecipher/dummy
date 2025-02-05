import boto3
import json
import re
import os
from datetime import datetime, timedelta

# AWS Clients
cloudtrail = boto3.client("cloudtrail")
ses = boto3.client("ses")

# Environment Variables (Set in Lambda)
SES_SENDER_EMAIL = os.environ["SES_SENDER_EMAIL"]  # Verified sender email

def lambda_handler(event, context):
    """Handles CloudFormation Drift Detection events."""
    print("Received Event:", json.dumps(event, indent=2))

    # Extract drifted stack name
    stack_name = event["detail"]["stack-name"]
    print(f"Drift detected in stack: {stack_name}")

    # Find the user who last updated this stack
    user_email = find_last_user(stack_name)
    
    if user_email:
        send_email(user_email, stack_name)
        return {"statusCode": 200, "body": f"Email sent to {user_email}"}
    
    return {"statusCode": 400, "body": "No valid user found"}

def find_last_user(stack_name):
    """Queries CloudTrail for the last user who updated the stack."""
    try:
        # Define the time range (last 7 days)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        # Query CloudTrail for UpdateStack events
        response = cloudtrail.lookup_events(
            LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": "UpdateStack"}],
            StartTime=start_time,
            EndTime=end_time,
            MaxResults=10  # Adjust based on usage
        )

        # Find matching stack updates
        for event in response["Events"]:
            event_details = json.loads(event["CloudTrailEvent"])
            if stack_name in event_details.get("requestParameters", {}).get("stackName", ""):
                print("Found matching event:", event_details)
                
                # Extract user identity
                user_identity = event_details["userIdentity"]
                return extract_email_from_identity(user_identity)

        print("No matching UpdateStack event found.")
        return None

    except Exception as e:
        print(f"Error querying CloudTrail: {str(e)}")
        return None

def extract_email_from_identity(user_identity):
    """Extracts 9-digit SSO and generates email."""
    try:
        username = user_identity.get("userName") or user_identity.get("arn", "").split("/")[-1]
        match = re.search(r"\b\d{9}\b", username)
        if match:
            sso = match.group()
            email = f"{sso}@company.com"
            print(f"Extracted SSO: {sso}, Email: {email}")
            return email

        print("No valid SSO found.")
        return None

    except Exception as e:
        print(f"Error extracting email: {str(e)}")
        return None

def send_email(user_email, stack_name):
    """Sends an email notification via AWS SES."""
    subject = "🚨 CloudFormation Stack Drift Alert"
    body = f"Hello,\n\nYour CloudFormation stack '{stack_name}' has drifted from its expected configuration.\n\nPlease review and take necessary actions."

    try:
        ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}}
            }
        )
        print(f"Email sent to {user_email}")

    except Exception as e:
        print(f"Error sending email: {str(e)}")
