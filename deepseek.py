import boto3
import time

# 🔹 Enter the stack name here
STACK_NAME = "your-stack-name-here"

cloudformation = boto3.client('cloudformation')

def detect_stack_drift(stack_name):
    """Check drift status and start detection only if necessary."""
    try:
        stack_info = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]
        drift_info = stack_info.get('DriftInformation', {})
        drift_status = drift_info.get('StackDriftStatus', 'UNKNOWN')

        if drift_status == "DETECTION_IN_PROGRESS":
            print(f"Drift detection already in progress for {stack_name}. Waiting...")
            while True:
                time.sleep(5)  # Reduced sleep time
                stack_info = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]
                drift_status = stack_info.get('DriftInformation', {}).get('StackDriftStatus', 'UNKNOWN')
                if drift_status != "DETECTION_IN_PROGRESS":
                    return drift_status

        if drift_status not in ["DRIFTED", "IN_SYNC"]:
            response = cloudformation.detect_stack_drift(StackName=stack_name)
            drift_detection_id = response['StackDriftDetectionId']
            print(f"🔄 Started drift detection for {stack_name}. Tracking progress...")

            # Wait for completion
            while True:
                time.sleep(5)
                stack_info = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]
                drift_status = stack_info.get('DriftInformation', {}).get('StackDriftStatus', 'UNKNOWN')
                if drift_status != "DETECTION_IN_PROGRESS":
                    return drift_status

    except Exception as e:
        print(f"⚠️ Error detecting drift for stack {stack_name}: {str(e)}")
        return None

def lambda_handler(event, context):
    """Lambda function to detect drift for one specific CloudFormation stack."""
    if not STACK_NAME:
        print("⚠️ No stack name provided. Please set STACK_NAME in the script.")
        return

    drift_status = detect_stack_drift(STACK_NAME)

    if drift_status in ["IN_SYNC", "DRIFTED"]:
        print(f"✅ CloudFormation Drift Status for {STACK_NAME}: {drift_status}")

    return {
        'statusCode': 200,
        'body': f'Drift detection completed for {STACK_NAME}.'
    }
