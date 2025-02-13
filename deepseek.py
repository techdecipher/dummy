import boto3

def lambda_handler(event, context):
    # Hardcode the SQS queue name here
    sqs_queue_name = "your-sqs-queue-name"  # Replace with your SQS queue name
    
    # Initialize boto3 clients
    sqs_client = boto3.client('sqs')
    cloudformation_client = boto3.client('cloudformation')
    
    try:
        # Get the SQS queue URL
        queue_url = sqs_client.get_queue_url(QueueName=sqs_queue_name)['QueueUrl']
        
        # Extract the queue ARN
        queue_arn = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['QueueArn']
        )['Attributes']['QueueArn']
        
        # List all CloudFormation stacks
        stacks = cloudformation_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE'])
        
        # Check if the queue ARN belongs to any stack
        for stack in stacks['StackSummaries']:
            stack_resources = cloudformation_client.list_stack_resources(StackName=stack['StackName'])
            for resource in stack_resources['StackResourceSummaries']:
                if resource.get('PhysicalResourceId') == queue_arn:
                    return {
                        'statusCode': 200,
                        'body': f'SQS queue {sqs_queue_name} belongs to stack {stack["StackName"]}'
                    }
        
        # If no stack is found
        return {
            'statusCode': 404,
            'body': f'SQS queue {sqs_queue_name} does not belong to any stack'
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
