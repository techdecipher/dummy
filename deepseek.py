import boto3
import time
import concurrent.futures

# Initialize the CloudFormation client
cloudformation = boto3.client('cloudformation')

def get_valid_stacks():
    """Retrieve all active stacks (excluding DELETE_COMPLETE and ROLLBACK_COMPLETE)."""
    stacks = []
    paginator = cloudformation.get_paginator('list_stacks')
    for page in paginator.paginate(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']):  
        stacks.extend(page['StackSummaries'])
    
    return [stack['StackName'] for stack in stacks]

def monitor_drift_detection(drift_detection_id):
    """Monitor drift detection progress until completion."""
    while True:
        response = cloudformation.describe_stack_drift_detection_status(StackDriftDetectionId=drift_detection_id)
        detection_status = response['DetectionStatus']

        if detection_status == "DETECTION_COMPLETE":
            return response['StackDriftStatus']
        
        elif detection_status == "DETECTION_FAILED":
            print(f"⚠️ Drift detection failed: {response.get('DetectionStatusReason', 'Unknown reason')}")
            return "UNKNOWN"

        time.sleep(2)  # Reduced wait time for faster execution

def detect_stack_drift(stack_name, attempt=1):
    """Trigger drift detection with exponential backoff to prevent throttling."""
    try:
        response = cloudformation.detect_stack_drift(StackName=stack_name)
        drift_detection_id = response['StackDriftDetectionId']
        print(f"🔄 Started drift detection for {stack_name}. Tracking progress...")

        return monitor_drift_detection(drift_detection_id)

    except Exception as e:
        error_message = str(e)
        if "Rate exceeded" in error_message and attempt <= 10:  # Increased max retries
            wait_time = 2 ** attempt  # Exponential backoff (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 seconds)
            print(f"⚠️ Throttling detected for {stack_name}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            return detect_stack_drift(stack_name, attempt + 1)

        print(f"⚠️ Error detecting drift for {stack_name}: {error_message}")
        return None

def lambda_handler(event, context):
    """Lambda function to trigger drift detection and only print IN_SYNC or DRIFTED stacks."""
    stack_names = get_valid_stacks()

    # Use ThreadPoolExecutor with reduced concurrency (max_workers=3)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(detect_stack_drift, stack_names))

    # Print results for stacks that are IN_SYNC or DRIFTED
    for stack_name, drift_status in zip(stack_names, results):
        if drift_status in ["IN_SYNC", "DRIFTED"]:
            print(f"✅ CloudFormation Drift Status for {stack_name}: {drift_status}")

    return {
        'statusCode': 200,
        'body': 'Drift detection completed for all stacks.'
    }
