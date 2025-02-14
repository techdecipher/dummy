import boto3
import json
import time

# Initialize AWS clients
cloudformation = boto3.client('cloudformation')
ses = boto3.client('ses')

# SES Configuration
SES_SENDER_EMAIL = "503356480@ge.com"
SES_SUBJECT = "AWS Drift Detected on Stack!"

def send_ses_notification(stack_name, instance_id, user_email):
    """Send an SES email when drift is detected."""
    try:
        email_body = (
            f"🚨 *Drift Detected!*\n\n"
            f"📌 *Stack Name:* {stack_name}\n"
            f"🔄 *EC2 Instance ID:* {instance_id}\n"
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

def find_stack(instance_id):
    """Find the CloudFormation stack managing the given EC2 instance."""
    try:
        stacks = cloudformation.list_stacks(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE"])
        for stack in stacks.get("StackSummaries", []):
            resources = cloudformation.list_stack_resources(StackName=stack["StackName"])
            for resource in resources.get("StackResourceSummaries", []):
                if resource["ResourceType"] == "AWS::EC2::Instance" and "PhysicalResourceId" in resource:
                    if resource["PhysicalResourceId"] == instance_id:
                        print(f"✅ EC2 Instance {instance_id} belongs to stack {stack['StackName']}")
                        return stack["StackName"]
        
        print(f"🚫 No valid stack found for EC2 instance {instance_id}. Skipping drift check.")
    except Exception as e:
        print(f"❌ Error finding stack for EC2 instance: {e}")
    return None

def check_drift(stack_name):
    """Check stack drift status with retry mechanism to handle in-progress detection."""
    try:
        # First get current Drift Status
        existing_drift_status = cloudformation.describe_stacks(StackName=stack_name)
        
        if existing_drift_status["Stacks"][0].get("DriftInformation", {}).get("StackDriftStatus") == "DETECTION_IN_PROGRESS":
            print(f"⚠️ Drift detection is already running for {stack_name}. Skipping new request.")
            return "IN_PROGRESS"

        # Second Start a New Drift Detection
        response = cloudformation.detect_stack_drift(StackName=stack_name)
        drift_id = response["StackDriftDetectionId"]

        # Third Wait and Check Status with Exponential Backoff
        wait_times = [10, 15, 20, 30, 40]  # Retry up to 5 times (total wait ~2 mins)
        
        for wait_time in wait_times:
            time.sleep(wait_time)
            drift_status = cloudformation.describe_stack_drift_detection_status(StackDriftDetectionId=drift_id)
            
            if drift_status["DetectionStatus"] == "DETECTION_COMPLETE":
                print(f"✅ Drift Check Complete for {stack_name}: {drift_status['StackDriftStatus']}")
                return drift_status["StackDriftStatus"]
            
            print(f"⏳ Waiting {wait_time} sec for drift detection to complete...")

        # Step 4: If Drift Detection Is Still In Progress, Send a Warning
        warning_message = (
            f"⚠️ Warning: Drift detection on Stack '{stack_name}' has been running for too long.\n"
            f"🚀 Please check CloudFormation manually."
        )
        print(warning_message)
        send_ses_notification(SES_SUBJECT_WARNING, warning_message, SES_SENDER_EMAIL)

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
    """Triggered by EventBridge when an EC2 instance is modified."""
    try:
        print("🔹 Received event:", json.dumps(event, indent=2))
        
        # Extract EC2 instance ID
        request_parameters = event.get("detail", {}).get("requestParameters", {})
        resource_items = request_parameters.get("resourcesSet", {}).get("items", [])
        instance_id = resource_items[0].get("resourceId") if resource_items else None
        
        if not instance_id:
            print("⚠️ No instanceId found in event. Possibly a DryRun request or malformed event.")
            return {"statusCode": 400, "body": "No valid EC2 instance found in event."}
        
        event_source = event["source"]
        if event_source != "aws.ec2":
            print("⚠️ Event is not related to EC2. Skipping.")
            return {"statusCode": 400, "body": "Unsupported event type"}

        user_identity = event["detail"]["userIdentity"]
        user_email = "Unknown User"
        if "userName" in user_identity:
            user_email = f"{user_identity['userName']}@ge.com"
        elif "arn" in user_identity:
            user_arn = user_identity["arn"]
            user_email = user_arn.split("/")[-1] + "@ge.com"

        request_params = event["detail"].get("requestParameters", {})

        # ✅ Handle different EC2 event types
        instance_id = None

        # For RunInstances event
        if "instancesSet" in request_params:
            instances_set = request_params["instancesSet"].get("items", [])
            if instances_set:
                instance_id = instances_set[0].get("instanceId")

        # For CreateTags event (Tagging EC2)
        elif "resourcesSet" in request_params:
            resources_set = request_params["resourcesSet"].get("items", [])
            if resources_set:
                instance_id = resources_set[0].get("resourceId")

        if not instance_id:
            print("⚠️ No instanceId found in event. Possibly a DryRun request or malformed event.")
            return {"statusCode": 400, "body": "Invalid event structure or DryRun request"}

        print(f"🔄 EC2 Instance Modified: {instance_id}, By User: {user_email}")

        stack_name = find_stack(instance_id)
        if stack_name:
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"🚨 Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, instance_id, user_email)
            else:
                print("✅ No drift detected.")

    except Exception as e:
        print(f"❌ Error processing event: {e}")

    return {"statusCode": 200, "body": "EC2 Drift detection complete."}
