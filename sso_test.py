import boto3
import os
import re

# Initialize SES client
ses = boto3.client("ses")

def get_user_email(user_identity):
    """Extracts 9-digit SSO from user identity and returns email."""
    try:
        print("Raw User Identity:", user_identity)

        # Extract username from userIdentity
        username = user_identity.get("userName") or user_identity.get("arn", "").split("/")[-1]
        print("Extracted Username:", username)

        # Match a 9-digit SSO
        match = re.search(r"\b\d{9}\b", username)
        if match:
            sso = match.group()
            email = f"{sso}@company.com"
            print("Extracted SSO:", sso)
            print("Generated Email:", email)
            return email
        else:
            print("No valid 9-digit SSO found in username.")
            return None
    except Exception as e:
        print("Error extracting email:", str(e))
        return None

def send_email(user_email):
    """Send an email using AWS SES"""
    sender_email = os.environ["SES_SENDER_EMAIL"]  # Get from environment variable
    subject = "CloudFormation Drift Alert"
    body = f"Hello,\n\nYour CloudFormation stack has been modified.\n\nPlease review the changes."

    try:
        response = ses.send_email(
            Source=sender_email,
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        print(f"Email sent successfully to {user_email}")
        return response
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return None

def lambda_handler(event, context):
    """Main entry point for AWS Lambda"""
    print("Lambda triggered with event:", event)

    # Extract user identity
    user_identity = event.get("detail", {}).get("userIdentity", {})
    
    # Get the email
    user_email = get_user_email(user_identity)
    
    if user_email:
        send_email(user_email)

    return {
        "statusCode": 200,
        "body": f"Email sent to {user_email}" if user_email else "No valid SSO found"
    }
