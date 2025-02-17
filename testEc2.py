import boto3
import json
import time

# AWS Clients
cloudformation = boto3.client("cloudformation")
ses = boto3.client("ses")

# SES Configuration
SES_SENDER_EMAIL = "503356480@gem.com"
SES_SUBJECT = "AWS Drift Detected on Stack!"


def send_ses_notification(stack_name, resource_name, user_email):
    """Send an SES email when drift is detected."""
    try:
        email_body = (
            f"Hello,\n\nA drift has been detected in the CloudFormation stack: {stack_name}.\n\n"
            f"Stack Name: {stack_name}\n"
            f"Resource Affected: {resource_name}\n"
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


def list_all_stacks():
    """Retrieve all CloudFormation stacks including paginated results."""
    stacks = []
    paginator = cloudformation.get_paginator("list_stacks")
    for page in paginator.paginate(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE"]):
        stacks.extend(page.get("StackSummaries", []))
    return stacks


def find_stack(resource_name, resource_type):
    """Find the CloudFormation stack managing the given resource, with pagination."""
    try:
        stacks = list_all_stacks()
        for stack in stacks:
            stack_name = stack["StackName"]
            paginator = cloudformation.get_paginator("list_stack_resources")
            for page in paginator.paginate(StackName=stack_name):
                for resource in page.get("StackResourceSummaries", []):
                    if resource["ResourceType"] == resource_type and resource.get("PhysicalResourceId"):
                        if resource_name in resource["PhysicalResourceId"]:  # Allow partial match
                            print(f" {resource_type} {resource_name} belongs to stack {stack_name}")
                            return stack_name

        print(f"No valid stack found for {resource_type} {resource_name}. Skipping drift check.")
    except Exception as e:
        print(f"Error finding stack for {resource_type}: {e}")
    return None


def check_drift(stack_name):
    """Ensures drift detection always runs and properly waits for completion."""
    try:
        # Attempt to Start Drift Detection
        try:
            response = cloudformation.detect_stack_drift(StackName=stack_name)
            drift_id = response["StackDriftDetectionId"]
            print(f"Started new drift detection for {stack_name}. ID: {drift_id}")
        except cloudformation.exceptions.ClientError as e:
            if "Drift detection is already in progress" in str(e):
                print(f"Drift detection already in progress for {stack_name}. Fetching latest drift status...")
            else:
                print(f"Error starting drift detection: {e}")
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
                print(f"Drift Check Complete for {stack_name}: {current_status}")
                return current_status

            print(f"Waiting for drift detection to complete... Attempt {retries + 1}/{max_retries}")
            retries += 1

        print(f"Drift check taking too long for {stack_name}. Check manually in CloudFormation.")
        return "UNKNOWN"

    except Exception as e:
        print(f"Error checking drift: {e}")
        return None


def lambda_handler(event, context):
    """Handles drift detection for CodePipeline, S3, and SQS."""
    try:
        print("Received event:", json.dumps(event, indent=2))

        event_source = event["source"]
        user_identity = event["detail"]["userIdentity"]

        # Extract user who triggered the event
        if "userName" in user_identity:
            user_email = f"{user_identity['userName']}@gem.com"
        elif "arn" in user_identity:
            user_arn = user_identity["arn"]
            user_email = user_arn.split("/")[-1] + "@gem.com"
        else:
            user_email = "Unknown User"

        # Handling CodePipeline Drift Detection
        if event_source == "aws.codepipeline":
            pipeline_name = event["detail"]["requestParameters"]["pipeline"]["name"]
            print(f"Pipeline Updated: {pipeline_name}, By User: {user_email}")

            stack_name = find_stack(pipeline_name, "AWS::CodePipeline::Pipeline")
            resource_name = pipeline_name

        # Handling S3 Drift Detection
        elif event_source == "aws.s3":
            s3_bucket_name = event["detail"]["requestParameters"]["bucketName"]
            print(f"S3 Bucket Modified: {s3_bucket_name}, By User: {user_email}")

            stack_name = find_stack(s3_bucket_name, "AWS::S3::Bucket")
            resource_name = s3_bucket_name

        # Handling SQS Drift Detection
        elif event_source == "aws.sqs":
            request_parameters = event.get("detail", {}).get("requestParameters", {})
            sqs_queue_url = request_parameters.get("queueUrl")
            if not sqs_queue_url:
                print("No SQS queue URL found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid SQS queue found in event."}

            sqs_queue_name = sqs_queue_url.split("/")[-1]
            print(f"SQS Queue Modified: {sqs_queue_name}, By User: {user_email}")

            stack_name = find_stack(sqs_queue_name, "AWS::SQS::Queue")
            resource_name = sqs_queue_name
        
        # Handling SNS Drift Detection
        elif event_source == "aws.sns":
            request_parameters = event.get("detail", {}).get("requestParameters", {})
            sns_topic_arn = request_parameters.get("topicArn")
            sns_topic_name = sns_topic_arn.split(":")[-1]
            print(f"SNS Topic Modified: {sns_topic_name}, By User: {user_email}")
            
            stack_name = find_stack(sns_topic_name, "AWS::SNS::Topic")
            resource_name = sns_topic_name
            
        else:
            print(f"Unhandled event source: {event_source}. Skipping.")
            return {"statusCode": 400, "body": "Unhandled event source"}

        if stack_name and stack_name != "NO_STACK_FOUND":
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, resource_name, user_email)
            else:
                print("No drift detected.")

    except Exception as e:
        print(f"Error processing event: {e}")

    return {"statusCode": 200, "body": "Drift detection complete."}
