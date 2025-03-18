import boto3
import json

codepipeline = boto3.client('codepipeline')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Extract pipeline details from the event
    pipeline_name = event['detail']['pipeline']
    execution_id = event['detail']['execution-id']
    
    # Get pipeline execution details
    execution_details = codepipeline.get_pipeline_execution(
        pipelineName=pipeline_name,
        pipelineExecutionId=execution_id
    )
    
    # Print basic information
    print(f'Pipeline Name: {pipeline_name}')
    print(f'Execution ID: {execution_id}')
    
    # Extract and print stage details
    stages = execution_details.get('pipelineExecution', {}).get('stages', [])
    if stages:
        print('Stages:')
        for stage in stages:
            print(json.dumps(stage, indent=2, default=str))
    else:
        print('No stage details available.')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Pipeline execution details captured successfully!')
    }
