import boto3
import time

# 🔹 Enter the stack name you want to check
STACK_NAME = "your-stack-name-here"

cloudformation = boto3.client('cloudformation')

def validate_stack_exists(stack_name):
    """Check if the provided stack exists before running drift detection."""
    try:
        cloudformation.describe_stacks(StackName=stack_name)
        return True
    except Exception as e:
        print(f"⚠️ Stack {stack_name} does not exist or is incorrect: {str(e)}")
        return False

def validate_stack_state(stack_name):
    """Check if the stack is in a valid state before running drift detection."""
    try:
        stack_info = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]
        stack_status = stack_info.get('StackStatus', '')

        if stack_status not in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
            print(f"⚠️ Stack {stack_name} is in state {stack_status}, drift detection not allowed.")
            return False

        return True
    except Exception as e:
        print(f"⚠️ Error checking stack state: {str(e)}")
        return False

def detect_stack_drift(stack_name):
    """Check drift status and start detection only if necessary."""
    try:
        stack_info = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]
        drift_info = stack_info.get('DriftInformation', {})
        drift_status = drift_info.get('StackDriftStatus', 'UNKNOWN')

        if drift_status == "DETECTION_IN_PROGRESS":
            print(f"Drift detection already in progress for {stack_name}. Waiting...")
            while True:
                time.sleep(5)
                stack_info = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]
                drift_status = stack_info.get('DriftInformation', {}).get('StackDriftStatus', 'UNKNOWN')
                if drift_status != "DETECTION_IN_PROGRESS":
                    return drift_status

        if drift_status not in ["DRIFTED", "IN_SYNC"]:
            response = cloudformation.detect_stack_drift(StackName=stack_name)

            if "StackDriftDetectionId" not in response:
                print(f"⚠️ AWS did not return a valid drift detection ID for {stack_name}.")
                return "ERROR: No detection ID"

            drift_detection_id = response['StackDriftDetectionId']
            print(f"🔄 Started drift detection for {stack_name}. Tracking progress...")

            while True:
                time.sleep(5)
                stack_info = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]
                drift_status = stack_info.get('DriftInformation', {}).get('StackDriftStatus', 'UNKNOWN')
                if drift_status != "DETECTION_IN_PROGRESS":
                    return drift_status

    except Exception as e:
        print(f"⚠️ Error detecting drift for stack {stack_name}: {str(e)}")
        return f"Error: {str(e)}"  

def lambda_handler(event, context):
    """Lambda function to detect drift for one specific CloudFormation stack."""
    print(f"🔹 Lambda execution started for stack: {STACK_NAME}")

    if not STACK_NAME:
        print("⚠️ No stack name provided. Please set STACK_NAME in the script.")
        return {'statusCode': 400, 'body': 'Error: No stack name provided.'}

    if not validate_stack_exists(STACK_NAME):
        return {'statusCode': 400, 'body': f'Error: Stack {STACK_NAME} does not exist.'}

    if not validate_stack_state(STACK_NAME):
        return {'statusCode': 400, 'body': f'Error: Stack {STACK_NAME} is in an unsupported state.'}

    drift_status = detect_stack_drift(STACK_NAME)

    if drift_status in ["IN_SYNC", "DRIFTED"]:
        print(f"✅ CloudFormation Drift Status for {STACK_NAME}: {drift_status}")
    else:
        print(f"⚠️ Unexpected result for {STACK_NAME}: {drift_status}")

    return {'statusCode': 200, 'body': f'Drift detection result for {STACK_NAME}: {drift_status}'}
