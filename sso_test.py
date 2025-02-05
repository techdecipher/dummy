import boto3
import json
import re
import os

# AWS Clients
ses = boto3.client("ses")  # AWS Simple Email Service
cloudtrail = boto3.client("cloudtrail")

# Environment Variables
SES_SENDER_EMAIL = os.environ["SES_SENDER_EMAIL"]  # Must be verified in SES

def lambda_handler(event, context):
    """Handles CloudFormation Drift Detection event, finds user, and sends email."""
    print("Lambda triggered with event:", event)  # Debugging print

    # ✅ Step 1: Extract Stack ID and Name
    stack_id = event["detail"].get("stack-id", "")
    if not stack_id:
        print("Error: No stack-id found in event!")
        return {"statusCode": 400, "body": "No stack-id found"}

    stack_name = stack_id.split("/")[-2]  # Extracting stack name from ARN
    print("Extracted Stack Name:", stack_name)  # Debugging print

    # ✅ Step 2: Get User from CloudTrail
    user_email = get_user_from_cloudtrail(stack_name)
    if not user_email:
        print(f"No user found for stack {stack_name}. Skipping email.")
        return {"statusCode": 200, "body": f"No user found for {stack_name}"}

    # ✅ Step 3: Send Email Notification
    send_email(user_email, stack_name)

    return {"statusCode": 200, "body": f"Drift notification sent to {user_email}"}

def get_user_from_cloudtrail(stack_name):
    """Fetches the IAM user who modified the given CloudFormation stack."""
    try:
        response = cloudtrail.lookup_events(
            LookupAttributes=[
                {"AttributeKey": "EventName", "AttributeValue": "UpdateStack"}
            ],
            MaxResults=5  # Fetch recent events
        )
        
        for event in response.get("Events", []):
            event_detail = json.loads(event["CloudTrailEvent"])
            user_identity = event_detail.get("userIdentity", {})
            username = user_identity.get("userName") or user_identity.get("arn", "").split("/")[-1]
            
            # ✅ Extract 9-digit SSO
            match = re.search(r"\b\d{9}\b", username)
            if match:
                sso = match.group()
                email = f"{sso}@company.com"
                print(f"Found User: {sso}, Email: {email}")
                return email

        print("No valid user found in CloudTrail events.")
        return None

    except Exception as e:
        print(f"Error retrieving user from CloudTrail: {e}")
        return None

def send_email(user_email, stack_name):
    """Sends an email notification via AWS SES."""
    subject = "⚠️ CloudFormation Stack Drift Alert"
    body = f"Hello,\n\nYour CloudFormation stack '{stack_name}' has drifted from its expected configuration.\n\nPlease review and fix the drift."

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
        print(f"Error sending email: {e}")
