import boto3
import json
import time

# AWS Clients
cloudformation = boto3.client("cloudformation")
ses = boto3.client("ses")

# SES Configuration
SES_SENDER_EMAIL = "503356480@xyz.com"
SES_SUBJECT = "🚨 AWS Drift Detected on Security Group!"

def send_ses_notification(stack_name, sg_id, user_email):
    """Send an SES email when drift is detected."""
    try:
        email_body = (
            f"🚨 *Drift Detected!*\n\n"
            f"📌 *Stack Name:* {stack_name}\n"
            f"🔒 *Security Group:* {sg_id}\n"
            f"👤 *User Responsible:* {user_email}\n\n"
            f"Check CloudFormation for further details."
        )

        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {"Data": SES_SUBJECT},
                "Body": {"Text": {"Data": email_body}},
            },
        )

        print(f"✅ SES Notification Sent to {user_email}! Message ID: {response['MessageId']}")

    except Exception as e:
        print(f"❌ Error sending SES email: {e}")

def list_all_stacks():
    """Retrieve all CloudFormation stacks including paginated results."""
    stacks = []
    paginator = cloudformation.get_paginator("list_stacks")
    for page in paginator.paginate(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE"]):
        stacks.extend(page.get("StackSummaries", []))
    return stacks

def find_stack(security_group_id):
    """Find the CloudFormation stack managing the given Security Group."""
    try:
        stacks = list_all_stacks()
        for stack in stacks:
            stack_name = stack["StackName"]
            paginator = cloudformation.get_paginator("list_stack_resources")
            for page in paginator.paginate(StackName=stack_name):
                for resource in page.get("StackResourceSummaries", []):
                    if resource["ResourceType"] == "AWS::EC2::SecurityGroup" and "PhysicalResourceId" in resource:
                        if resource["PhysicalResourceId"] == security_group_id:
                            print(f"✅ Security Group {security_group_id} belongs to stack {stack_name}")
                            return stack_name

        print(f"🚫 No valid stack found for Security Group {security_group_id}. Skipping drift check.")
    except Exception as e:
        print(f"❌ Error finding stack for Security Group: {e}")

    return "NO_STACK_FOUND"

def check_drift(stack_name):
    """Ensures drift detection always runs and properly waits for completion."""
    try:
        # Step 1: Always Attempt to Start Drift Detection
        try:
            response = cloudformation.detect_stack_drift(StackName=stack_name)
            drift_id = response["StackDriftDetectionId"]
            print(f"🚀 Started new drift detection for {stack_name}. ID: {drift_id}")
        except cloudformation.exceptions.ClientError as e:
            if "Drift detection is already in progress" in str(e):
                print(f"⚠️ Drift detection already in progress for {stack_name}. Fetching latest drift status...")
            else:
                print(f"❌ Error starting drift detection: {e}")
                return None

        # Step 2: Periodically Check Status Until It Completes
        wait_times = [10, 15, 20, 30, 40]  # Retry with increasing wait times
        retries = 0
        max_retries = 10  # Extend retries (~5 minutes max wait)

        while retries < max_retries:
            time.sleep(wait_times[min(retries, len(wait_times) - 1)])  # Adaptive wait time
            drift_status = cloudformation.describe_stacks(StackName=stack_name)
            current_status = drift_status["Stacks"][0].get("DriftInformation", {}).get("StackDriftStatus")

            if current_status in ["IN_SYNC", "DRIFTED"]:
                print(f"✅ Drift Check Complete for {stack_name}: {current_status}")
                return current_status

            print(f"⏳ Waiting for drift detection to complete... Attempt {retries + 1}/{max_retries}")
            retries += 1

        print(f"⚠️ Drift check taking too long for {stack_name}. Check manually in CloudFormation.")
        return "UNKNOWN"

    except Exception as e:
        print(f"❌ Error checking drift: {e}")
        return None

def lambda_handler(event, context):
    """Triggered by EventBridge when a Security Group is modified."""
    try:
        print("🔹 Received event:", json.dumps(event, indent=2))

        request_parameters = event.get("detail", {}).get("requestParameters", {})
        sg_id = request_parameters.get("groupId")
        if not sg_id:
            print("⚠️ No Security Group ID found in event. Skipping.")
            return {"statusCode": 400, "body": "No valid Security Group found in event."}

        user_identity = event["detail"]["userIdentity"]

        # Extract user who triggered the event
        if "userName" in user_identity:
            user_email = f"{user_identity['userName']}@xyz.com"
        elif "arn" in user_identity:
            user_arn = user_identity["arn"]
            user_email = user_arn.split("/")[-1] + "@xyz.com"
        else:
            user_email = "Unknown User"

        print(f"🔒 Security Group Modified: {sg_id}, By User: {user_email}")

        stack_name = find_stack(sg_id)
        if stack_name != "NO_STACK_FOUND":
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"🚨 Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, sg_id, user_email)
            else:
                print("✅ No drift detected.")

    except Exception as e:
        print(f"❌ Error processing event: {e}")

    return {"statusCode": 200, "body": "Security Group Drift detection complete."}
