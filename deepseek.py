import boto3
import time

# 🔹 Enter the stack name here
STACK_NAME = "testses"

cloudformation = boto3.client('cloudformation')

def detect_stack_drift(stack_name, attempt=1):
    """Force drift detection every time Lambda runs."""
    try:
        # Step 1: Always trigger drift detection
        response = cloudformation.detect_stack_drift(StackName=stack_name)
        drift_detection_id = response.get('StackDriftDetectionId')
        if not drift_detection_id:
            print(f"⚠️ No DriftDetectionId returned for {stack_name}.")
            return "ERROR: No detection ID"

        print(f"🔄 Started drift detection for {stack_name}. Tracking progress...")

        # Step 2: Wait for drift detection to complete
        while True:
            time.sleep(5)
            status_response = cloudformation.describe_stack_drift_detection_status(StackDriftDetectionId=drift_detection_id)
            detection_status = status_response['DetectionStatus']

            if detection_status == "DETECTION_COMPLETE":
                return status_response['StackDriftStatus']
            elif detection_status == "DETECTION_FAILED":
                return f"⚠️ Drift detection failed: {status_response.get('DetectionStatusReason', 'Unknown reason')}"

    except Exception as e:
        error_message = str(e)

        # Step 3: Handle Rate Limit Issues (Retry with Exponential Backoff)
        if "Rate exceeded" in error_message and attempt <= 5:
            wait_time = 2 ** attempt  # Exponential backoff (2, 4, 8, 16, 32 seconds)
            print(f"⚠️ Rate limit hit. Retrying {stack_name} in {wait_time} seconds...")
            time.sleep(wait_time)
            return detect_stack_drift(stack_name, attempt + 1)

        print(f"⚠️ Error detecting drift for {stack_name}: {error_message}")
        return f"Error: {error_message}"

def lambda_handler(event, context):
    """Lambda function to force detect drift for a specific CloudFormation stack."""
    print(f"🔹 Lambda execution started for stack: {STACK_NAME}")

    drift_status = detect_stack_drift(STACK_NAME)

    if drift_status in ["IN_SYNC", "DRIFTED"]:
        print(f"✅ CloudFormation Drift Status for {STACK_NAME}: {drift_status}")
    else:
        print(f"⚠️ Unexpected result for {STACK_NAME}: {drift_status}")

    return {
        'statusCode': 200,
        'body': f'Drift detection result for {STACK_NAME}: {drift_status}'
    }
