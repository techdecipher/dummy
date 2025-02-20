import boto3
import json
import time

# AWS Clients
cloudformation = boto3.client("cloudformation")
ses = boto3.client("ses")

# SES Configuration
SES_SENDER_EMAIL = "pranav.chaudhari@gem.com"
SES_SUBJECT = "🚨 AWS Drift Detected!"

# Mapping AWS Account ID to AWS Account Type
ACCOUNT_TYPE_MAPPING = {
    "111111111111": "Innovation",
    "222222222222": "Production",
    "333333333333": "Development",
}

def check_drift(stack_name):
    """Ensures drift detection always runs and properly waits for completion."""
    try:
        # Start Drift Detection
        response = cloudformation.detect_stack_drift(StackName=stack_name)
        drift_id = response["StackDriftDetectionId"]
        print(f"🚀 Started new drift detection for {stack_name}. ID: {drift_id}")

        # Wait and Check Status Until It Completes
        retries, max_retries = 0, 10
        wait_times = [10, 15, 20, 30, 40]

        while retries < max_retries:
            time.sleep(wait_times[min(retries, len(wait_times) - 1)]) 
            drift_status = cloudformation.describe_stacks(StackName=stack_name)
            current_status = drift_status["Stacks"][0].get("DriftInformation", {}).get("StackDriftStatus")

            if current_status in ["IN_SYNC", "DRIFTED"]:
                drift_time = drift_status["Stacks"][0].get("LastUpdatedTime", "Unknown Time")
                print(f"✅ Drift Check Complete for {stack_name}: {current_status} at {drift_time}")
                return current_status, drift_time

            retries += 1
            print(f"⏳ Waiting for drift detection... Attempt {retries}/{max_retries}")

        return "UNKNOWN", "Unknown Time"

    except Exception as e:
        print(f"❌ Error checking drift: {e}")
        return None, "Unknown Time"


def send_ses_notification(stack_name, resource_name, resource_type, user_email, event, drift_time):
    """Send an SES email using the required HTML template for drift detection."""
    try:
        # Extract details from the event
        aws_account_id = event.get("recipientAccountId", "Unknown")
        agent = event["detail"].get("userAgent", "Unknown Agent")

        # Get AWS Account Type
        aws_account_type = ACCOUNT_TYPE_MAPPING.get(aws_account_id, "Unknown")

        # Extract user identity details
        user_identity = event["detail"]["userIdentity"]
        user_sso = user_identity.get("userName", "Unknown SSO")
        federated_role = user_identity.get("arn", "Unknown Role")

        # Define the HTML email template
        email_body = f"""
        <html>
        <body>
            <table border="2px" align="center" style="font-family: 'Gill Sans', Calibri; background-color:white;font-size: 17px;" width="650px">
                <tr><td colspan="5" align="center" style="background-color: #3972B9;color: white;font-size: 19px;"><b>AWS Drift Detection Alerts</b></td></tr>
                <tr><td colspan="5" align="center" style="font-size: 15px;">You are receiving this mail because you are part of the AWS Admin Team</td></tr>
                
                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;" >Alert Description</td></tr>
                <tr><td colspan="5" align="center" style="font-size:15px;">User <b>{user_sso}</b> has made a change on the stack <b>{stack_name}</b></td></tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;" >Object Impacted</td></tr>
                <tr><td colspan="5" align="center" style="font-size:15px;">{resource_name}</td></tr>

                <tr><td colspan="3" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;"><b>Timestamp of Change (UTC)</b></td>
                    <td colspan="2" align="center" style="font-size:15px;">{drift_time}</td></tr>
                
                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;">Action Message</td></tr>
                <tr><td colspan="5" style="text-align: center;color:red;">Please review and take necessary action to restore the changes.</td></tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;" >Details of the Change</td></tr>
                <tr><td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">AWS Account</td>
                    <td colspan="3" style="text-align: center;font-size:15px;color: orange;"><b>{aws_account_type}</b></td></tr>

                <tr><td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">Resource Type</td>
                    <td colspan="3" style="text-align: center;font-size:15px;">{resource_type}</td></tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;">Change Triggered By</td></tr>
                <tr>
                    <td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">User SSO</td>
                    <td style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">Role Used</td>
                    <td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">Agent</td>
                </tr>
                <tr>
                    <td colspan="2" align="center" style="font-size: 15px;">{user_sso}</td>
                    <td align="center" style="font-size: 15px;">{federated_role}</td>
                    <td colspan="2" align="center" style="font-size: 15px;">{agent}</td>
                </tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;">DevOps Team</td></tr>
            </table>
        </body>
        </html>
        """

        # Send the email using SES
        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {"Data": SES_SUBJECT, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": email_body, "Charset": "UTF-8"}
                },
            },
        )

        print(f"✅ SES Notification Sent to {user_email}! Message ID: {response['MessageId']}")

    except Exception as e:
        print(f"❌ Error sending SES email: {e}")


# Example Usage in Lambda Function
def lambda_handler(event, context):
    """Handles CodePipeline drift detection."""
    try:
        print("🔹 Received event:", json.dumps(event, indent=2))

        event_source = event["source"]
        if event_source == "aws.codepipeline":
            pipeline_name = event["detail"]["requestParameters"]["pipeline"]["name"]
            stack_name = pipeline_name
            resource_name = pipeline_name
            resource_type = "AWS::CodePipeline::Pipeline"

            drift_result, drift_time = check_drift(stack_name)
            if drift_result == "DRIFTED":
                send_ses_notification(stack_name, resource_name, resource_type, "user@example.com", event, drift_time)

    except Exception as e:
        print(f"❌ Error processing event: {e}")
