import boto3
 
def lambda_handler(event, context):
    ec2_client = boto3.client("ec2")
 
    # Define the tag key to filter instances
    
