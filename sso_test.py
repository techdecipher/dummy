import boto3
import json
import re
import os

# AWS Clients
cloudtrail = boto3.client("cloudtrail")

def lambda_handler(event, context):
    """Handles CloudFormation Drift Detection event and finds user."""
    print("Lambda triggered with event:", json.dumps(event, indent=2))  # Debugging print

    # ✅ Step 1: Validate the event (Only process drifted stacks)
    if event["detail"].get("status-details", {}).get("stack-drift-status") != "DRIFTED":
        print("No drift detected. Exiting.")
        return {"statusCode": 200, "body": "No drift detected"}

    # ✅ Step 2: Extract Stack ID and Name
    stack_id = event["detail"].get("stack-id", "")
    if not stack_id:
        print("Error: No stack-id found in event!")
        return {"statusCode": 400, "body": "No stack-id found"}

    stack_name = stack_id.split("/")[-2]  # Extract stack name from ARN
    print("Extracted Stack Name:", stack_name)  # Debugging print

    # ✅ Step 3: Get User from CloudTrail
    user_email = get_user_from_cloudtrail(stack_name)
    if not user_email:
        print(f"No user found for stack {stack_name}. Skipping email.")
        return {"statusCode": 200, "body": f"No user found for {stack_name}"}

    # ✅ Step 4: Just Print User Instead of Sending Email
    print(f"Detected User Email: {user_email}")

    return {"statusCode": 200, "body": f"Detected User Email: {user_email}"}

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
