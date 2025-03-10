import json
import re  # Import regex for SSO validation

def lambda_handler(event, context):
    """Handles drift detection according to the Services"""
    try:
        print("Received event:", json.dumps(event, indent=2))

        # Getting necessary details
        event_source = event["source"]
        user_identity = event["detail"]["userIdentity"]
        recipient_account_id = event["detail"].get("recipientAccountId")
        aws_account_type = ACCOUNT_TYPE_MAPPING.get(recipient_account_id)
        agent = event["detail"].get("userAgent", "Unknown Agent")
        federated_role_arn = user_identity.get("arn", "Unknown Role")
        federated_role = federated_role_arn.split("assumed-role/")[-1].split("/")[0]
        event_time = event["detail"].get("eventTime")

        # Extract user of the event who triggered it
        if "userName" in user_identity:
            user_sso = user_identity["userName"]
            user_email = f"{user_sso}@yoyo.com"
        elif "arn" in user_identity:
            user_arn = user_identity["arn"]
            user_sso = user_arn.split("/")[-1]
            user_email = f"{user_sso}@yoyo.com"
        else:
            user_sso = "Unknown"
            user_email = "Unknown User"

        # **🔹 NEW: Skip processing for non-SSO users (Exit Early)**
        if not re.match(r"^\d{9}$", user_sso):  # Check if user_sso is NOT a 9-digit number
            print(f"Skipping drift check for non-SSO user: {user_sso}")
            return {"statusCode": 200, "body": f"Skipped processing for non-SSO user: {user_sso}"}

        print(f"Processing drift detection for SSO user: {user_sso}")

        # Handle CodePipeline Drift Detection
        if event_source == "aws.codepipeline":
            pipeline_name = event["detail"]["requestParameters"]["pipeline"]["name"]
            print(f"Pipeline Updated: {pipeline_name}, By User: {user_email}")

            stack_name = find_stack(pipeline_name, "AWS::CodePipeline::Pipeline")
            resource_name = pipeline_name
            event_type = "CodePipeline"

        # Handle S3 Drift Detection
        elif event_source == "aws.s3":
            s3_bucket_name = event["detail"]["requestParameters"]["bucketName"]
            print(f"S3 Bucket Modified: {s3_bucket_name}, By User: {user_email}")

            stack_name = find_stack(s3_bucket_name, "AWS::S3::Bucket")
            resource_name = s3_bucket_name
            event_type = "S3 Bucket"

        # Handle any other services drift detection (Can be extended)
            
        # If no event matched else handle it gracefully
        else:
            print(f"Unhandled event source: {event_source}. Skipping.")
            return {"statusCode": 400, "body": "Unhandled event source"}
        
        # Send email when Stack found to be Drifted
        if stack_name and stack_name != "NO_STACK_FOUND":
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, resource_name, user_sso, aws_account_type, federated_role, agent, event_type, user_email, event_time)
            else:
                print("No drift detected.")

    except Exception as e:
        print(f"Error processing event: {e}")

    return {"statusCode": 200, "body": "Drift detection complete."}
