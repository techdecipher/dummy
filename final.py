import boto3
import json

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    instance_id = event["detail"]["instance-id"]
    instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]

    tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
    
    if tags.get("Vendor") == "Databricks":
        print(f"Databricks instance detected: {instance_id}")

    return {"status": "success", "instance_id": instance_id}
