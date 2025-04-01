import boto3
import json
import datetime

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    az = 'us-east-1a'                            # Target Availability Zone
    region = 'us-east-1'                         # Region
    bucket = 'your-s3-bucket-name'               # Replace with your S3 bucket name

    
