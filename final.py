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
    
    print(f'Execution Details: {json.dumps(execution_details, indent=2)}')
    summary = execution_details.get('pipelineExecution', {})
    print(summary)

    # Get the pipeline details
    response = codepipeline.get_pipeline(name=pipeline_name)
    print(response)    
    # Extract the required details
    pipeline_details = response['pipeline']
    name = pipeline_details['name']
    stages = pipeline_details['stages']
        
    # Log the details
    print('Stages:')
    # Extract and print stage details
    #stage_states = execution_details.get('pipelineExecution', {}).get('stage_states', [])
    #stages = execution_details['pipelineExecution']['stages']
    #print(stages)

    stages = execution_details['pipelineExecution']['stages']
        for stage in stages:
            if stage['name'] == 'Airflow-Source':
                for action in stage['actions']:
                    if 'output' in action:
                        output_variables = action['output']['outputVariables']
                        
                        # Extract and print the desired attributes
                        author_date = output_variables.get('AuthorDate', 'Unknown')
                        author_display_name = output_variables.get('AuthorDisplayName', 'Unknown')
                        author_email = output_variables.get('AuthorEmail', 'Unknown')
                        author_id = output_variables.get('AuthorId', 'Unknown')
                        branch_name = output_variables.get('BranchName', 'Unknown')
                        commit_id = output_variables.get('CommitId', 'Unknown')
                        commit_message = output_variables.get('CommitMessage', 'Unknown')
                        connection_arn = output_variables.get('ConnectionArn', 'Unknown')
                        full_repository_name = output_variables.get('FullRepositoryName', 'Unknown')
                        provider_type = output_variables.get('ProviderType', 'Unknown')
    return {
        'statusCode': 200,
        'body': json.dumps('Pipeline execution details captured successfully!')
    }
