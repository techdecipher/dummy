import boto3
import json
import time

# AWS Clients
cloudformation = boto3.client('cloudformation')
ses = boto3.client('ses')

# SES Configuration
SES_SENDER_EMAIL = "503356480@ge.com"
SES_SUBJECT = "AWS Drift Detected on Stack!"

def send_ses_notification(stack_name, resource_name, user_email):
    """Send an SES email when drift is detected."""
    try:
        email_body = (
            f"Hello,\n\nA drift has been detected in the CloudFormation stack: {stack_name}.\n\n"
            f"Stack Name: {stack_name}\n"
            f"Resource Afftected: {resource_name}\n"
            f"User Responsible: {user_email}\n\n"
            "Please review and take necessary action.\n\nBest Regards,\nDevOps Team"
        )

        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [user_email]},  
            Message={
                "Subject": {"Data": SES_SUBJECT},
                "Body": {"Text": {"Data": email_body}},
            },
        )

        print(f"SES Notification Sent to {user_email}! Message ID: {response['MessageId']}")

    except Exception as e:
        print(f"Error sending SES email: {e}")

def find_stack(resource_name, resource_type):
    """Find the CloudFormation stack managing the given resource."""
    try:
        stacks = cloudformation.list_stacks(
            StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE"]
        )
        for stack in stacks.get("StackSummaries", []):
            resources = cloudformation.list_stack_resources(StackName=stack["StackName"])
            for resource in resources.get("StackResourceSummaries", []):
                if resource["ResourceType"] == resource_type and resource.get("PhysicalResourceId") == resource_name:
                    print(f"{resource_type} {resource_name} belongs to stack {stack['StackName']}")
                    return stack["StackName"]

        print(f"No valid stack found for {resource_type} {resource_name}. Skipping drift check.")
    except Exception as e:
        print(f"Error finding stack for {resource_type}: {e}")
    return None

def check_drift(stack_name):
    """Check stack drift status with retry mechanism to handle in-progress detection."""
    try:
        existing_drift_status = cloudformation.describe_stacks(StackName=stack_name)
        
        if existing_drift_status["Stacks"][0].get("DriftInformation", {}).get("StackDriftStatus") == "DETECTION_IN_PROGRESS":
            print(f"Drift detection is already running for {stack_name}. Skipping new request.")
            return "IN_PROGRESS"

        response = cloudformation.detect_stack_drift(StackName=stack_name)
        drift_id = response["StackDriftDetectionId"]

        time.sleep(10)  
        for _ in range(5):  
            drift_status = cloudformation.describe_stack_drift_detection_status(StackDriftDetectionId=drift_id)
            
            if drift_status["DetectionStatus"] == "DETECTION_COMPLETE":
                print(f"Drift Check Complete for {stack_name}: {drift_status['StackDriftStatus']}")
                return drift_status["StackDriftStatus"]
            
            print("Waiting for drift detection to complete...")
            time.sleep(10)  

        print(f"Drift check taking too long for {stack_name}. Check manually in CloudFormation.")
        return "UNKNOWN"

    except cloudformation.exceptions.ClientError as e:
        error_message = str(e)
        if "Drift detection is already in progress" in error_message:
            print(f"Drift detection already in progress for {stack_name}. Skipping.")
            return "IN_PROGRESS"
        else:
            print(f"Error checking drift: {error_message}")
            return None

def lambda_handler(event, context):
    """Handles both CodePipeline and S3 drift detection."""
    try:
        print("Received event:", json.dumps(event, indent=2))

        event_source = event["source"]
        user_identity = event["detail"]["userIdentity"]

        # Extract user
        if "userName" in user_identity:
            user_email = f"{user_identity['userName']}@xyz.com"
        elif "arn" in user_identity:
            user_arn = user_identity["arn"]
            user_email = user_arn.split("/")[-1] + "@xyz.com"
        else:
            user_email = "Unknown User"

        if event_source == "aws.codepipeline":
            pipeline_name = event["detail"]["requestParameters"]["pipeline"]["name"]
            print(f"CodePipeline Updated: {pipeline_name}, By User: {user_email}")

            stack_name = find_stack(pipeline_name, "AWS::CodePipeline::Pipeline")
            resource_name = pipeline_name

        elif event_source == "aws.s3":
            s3_bucket_name = event["detail"]["requestParameters"]["bucketName"]
            print(f"S3 Bucket Modified: {s3_bucket_name}, By User: {user_email}")

            stack_name = find_stack(s3_bucket_name, "AWS::S3::Bucket")
            resource_name = s3_bucket_name

        else:
            print(f"Unhandled event source: {event_source}")
            return {"statusCode": 400, "body": "Unhandled event source"}

        if stack_name:
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, resource_name, user_email)
            else:
                print("No drift detected.")

    except Exception as e:
        print(f"Error processing event: {e}")

    return {"statusCode": 200, "body": "Drift detection complete."}
