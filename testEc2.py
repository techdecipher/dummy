import boto3
import json
import time

# Initialize AWS clients
cloudformation = boto3.client('cloudformation')
ses = boto3.client('ses')

# SES Configuration
SES_SENDER_EMAIL = "503356480@ge.com"
SES_SUBJECT = "🚨 AWS Drift Detected!"

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
    """Triggered by EventBridge when an EC2 instance is modified."""
    try:
        print("🔹 Received event:", json.dumps(event, indent=2))
        
        request_parameters = event.get("detail", {}).get("requestParameters", {})
        
        # ✅ Extract EC2 instance ID from event
        instance_id = None
        if "instancesSet" in request_parameters:
            instances_set = request_parameters["instancesSet"].get("items", [])
            if instances_set:
                instance_id = instances_set[0].get("instanceId")

        if not instance_id and "resourcesSet" in request_parameters:
            resources_set = request_parameters["resourcesSet"].get("items", [])
            if resources_set:
                instance_id = resources_set[0].get("resourceId")

        if not instance_id:
            print("⚠️ No instanceId found in event. Possibly a DryRun request or malformed event.")
            return {"statusCode": 400, "body": "No valid EC2 instance found in event."}

        user_identity = event["detail"]["userIdentity"]
        user_email = f"{user_identity.get('userName', 'unknown')}@xyz.com"

        print(f"🔄 EC2 Instance Modified: {instance_id}, By User: {user_email}")

        stack_name = find_stack(instance_id)
        if stack_name != "NO_STACK_FOUND":
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"🚨 Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, instance_id, user_email)
            else:
                print("✅ No drift detected.")

    except Exception as e:
        print(f"❌ Error processing event: {e}")

    return {"statusCode": 200, "body": "EC2 Drift detection complete."}
