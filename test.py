import boto3
import json

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))
