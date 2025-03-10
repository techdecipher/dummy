import boto3
import json

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Log the received event
    print("Received event:", json.dumps(event, indent=2))

    # Extract instance ID from the EventBridge event
    instance_id = event['detail']['instance-id']
    
    # Fetch instance details
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]

    # Check if it's a Databricks instance
    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
    if 'databricks-instance-type' in tags:
        print(f"Instance {instance_id} identified as Databricks instance. Updating tags.")

        # Update tags
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[{'Key': 'ManagedBy', 'Value': 'Lambda-Script'}]  # Modify as needed
        )

    return {"status": "success", "instance_id": instance_id}
