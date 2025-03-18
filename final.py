import boto3
import json

codepipeline = boto3.client('codepipeline')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Extract pipeline details
    pipeline_name = event['detail']['pipeline']
    execution_id = event['detail']['execution-id']
    
    # Get pipeline execution details
    execution_details = codepipeline.get_pipeline_execution(
        pipelineName=pipeline_name,
        pipelineExecutionId=execution_id
    )
    
    # Extract output artifact details
    print(f'Pipeline Name: {pipeline_name}')
    print(f'Execution ID: {execution_id}')
    print('Stages:')
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Pipeline execution details captured successfully!')
    }
