import boto3
import time

cloudformation = boto3.client('cloudformation')

def get_all_stacks():
    """Retrieve all CloudFormation stacks that are not in DELETE_COMPLETE state."""
    stacks = []
    paginator = cloudformation.get_paginator('list_stacks')
    for page in paginator.paginate(StackStatusFilter=[
        'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE', 'ROLLBACK_COMPLETE'
    ]):
        stacks.extend(page['StackSummaries'])
    return [stack['StackName'] for stack in stacks]

def detect_stack_drift(stack_name):
    """Detect drift for a specific stack and return the drift status."""
    response = cloudformation.detect_stack_drift(StackName=stack_name)
    drift_detection_id = response['StackDriftDetectionId']
    
    # Wait for drift detection to complete
    while True:
        drift_status = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]['DriftInformation']['StackDriftStatus']
        if drift_status != "DETECTION_IN_PROGRESS":
            break
        time.sleep(10)  # Wait before checking again
    
    return drift_status

def lambda_handler(event, context):
    """Lambda function to detect drift for all CloudFormation stacks."""
    stack_names = get_all_stacks()
    
    for stack_name in stack_names:
        drift_status = detect_stack_drift(stack_name)
        
        # Print drift status to logs (CloudWatch)
        print(f"CloudFormation Drift Status for {stack_name}: {drift_status}")
    
    return {
        'statusCode': 200,
        'body': 'Drift detection completed for all stacks.'
    }
