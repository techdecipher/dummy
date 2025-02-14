import boto3
import json
import time

# Initialize AWS clients
cloudformation = boto3.client('cloudformation')
ses = boto3.client('ses')

# SES Configuration
SES_SENDER_EMAIL = "503356480@ge.com"
SES_SUBJECT = "🚨 AWS Drift Detected!"

def send_ses_notification(stack_name, sqs_queue, user_email):
    """Send an SES email when drift is detected."""
    try:
        email_body = (
            f"🚨 *Drift Detected!*\n\n"
            f"📌 *Stack Name:* {stack_name}\n"
            f"🔄 *SQS Queue:* {sqs_queue}\n"
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

def find_stack(sqs_queue_name):
    """Find the CloudFormation stack managing the given SQS queue."""
    try:
        stacks = cloudformation.list_stacks(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE"])
        for stack in stacks.get("StackSummaries", []):
            resources = cloudformation.list_stack_resources(StackName=stack["StackName"])
            for resource in resources.get("StackResourceSummaries", []):
                if resource["ResourceType"] == "AWS::SQS::Queue" and "PhysicalResourceId" in resource:
                    if resource["PhysicalResourceId"].endswith(sqs_queue_name):
                        print(f"✅ SQS Queue {sqs_queue_name} belongs to stack {stack['StackName']}")
                        return stack["StackName"]
        
        print(f"🚫 No valid stack found for SQS queue {sqs_queue_name}. Skipping drift check.")
    except Exception as e:
        print(f"❌ Error finding stack for SQS queue: {e}")
    
    return "NO_STACK_FOUND"

def check_drift(stack_name):
    """Check stack drift status with retry mechanism to handle in-progress detection."""
    try:
        existing_drift_status = cloudformation.describe_stacks(StackName=stack_name)
        
        if existing_drift_status["Stacks"][0].get("DriftInformation", {}).get("StackDriftStatus") == "DETECTION_IN_PROGRESS":
            print(f"⚠️ Drift detection is already running for {stack_name}. Skipping new request.")
            return "IN_PROGRESS"

        response = cloudformation.detect_stack_drift(StackName=stack_name)
        drift_id = response["StackDriftDetectionId"]

        wait_times = [10, 15, 20, 30, 40]  # Retry up to 5 times (~2 mins total wait)
        
        for wait_time in wait_times:
            time.sleep(wait_time)
            drift_status = cloudformation.describe_stack_drift_detection_status(StackDriftDetectionId=drift_id)
            
            if drift_status["DetectionStatus"] == "DETECTION_COMPLETE":
                print(f"✅ Drift Check Complete for {stack_name}: {drift_status['StackDriftStatus']}")
                return drift_status["StackDriftStatus"]
            
            print(f"⏳ Waiting {wait_time} sec for drift detection to complete...")

        print(f"⚠️ Drift check taking too long for {stack_name}. Check manually in CloudFormation.")
        return "UNKNOWN"

    except cloudformation.exceptions.ClientError as e:
        error_message = str(e)
        if "Drift detection is already in progress" in error_message:
            print(f"⚠️ Drift detection already in progress for {stack_name}. Skipping.")
            return "IN_PROGRESS"
        else:
            print(f"❌ Error checking drift: {error_message}")
            return None

def lambda_handler(event, context):
    """Triggered by EventBridge when an SQS queue is modified."""
    try:
        print("🔹 Received event:", json.dumps(event, indent=2))

        request_parameters = event.get("detail", {}).get("requestParameters", {})
        sqs_queue_url = request_parameters.get("queueUrl")
        if not sqs_queue_url:
            print("⚠️ No SQS queue URL found in event. Skipping.")
            return {"statusCode": 400, "body": "No valid SQS queue found in event."}

        sqs_queue_name = sqs_queue_url.split("/")[-1]

        user_identity = event["detail"]["userIdentity"]
        
        # Extract user who triggered the event
        if "userName" in user_identity:
            user_email = f"{user_identity['userName']}@xyz.com"
        elif "arn" in user_identity:
            user_arn = user_identity["arn"]
            user_email = user_arn.split("/")[-1] + "@xyz.com"
        else:
            user_email = "Unknown User"

        print(f"🔄 SQS Queue Modified: {sqs_queue_name}, By User: {user_email}")

        stack_name = find_stack(sqs_queue_name)
        if stack_name != "NO_STACK_FOUND":
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"🚨 Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, sqs_queue_name, user_email)
            else:
                print("✅ No drift detected.")

    except Exception as e:
        print(f"❌ Error processing event: {e}")

    return {"statusCode": 200, "body": "SQS Drift detection complete."}
