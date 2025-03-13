import boto3
import json

ec2_client = boto3.client("ec2")

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    instance_id = event["detail"]["instance-id"]

    # Fetch instance details
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = response["Reservations"][0]["Instances"][0]

    # Extract tags
    tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}

    # Check if instance has Vendor=Databricks
    if tags.get("Vendor") == "Databricks":
        print(f"Databricks instance detected: {instance_id}")

        # Add the new tag "NoBackup=true"
        ec2_client.create_tags(
            Resources=[instance_id],
            Tags=[{"Key": "NoBackup", "Value": "true"}]
        )
        print(f"Tagged instance {instance_id} with NoBackup=true")
    else:
        print(f"Instance {instance_id} does not have Vendor=Databricks, skipping.")

    return {"status": "success", "instance_id": instance_id}
