import boto3
 
def lambda_handler(event, context):
    ec2_client = boto3.client("ec2")
 
    # Define the tag key to filter instances
    tag_key = "Vendor"  # Change this to the tag you want to filter by
 
    response = ec2_client.describe_instances(
        Filters=[{"Name": f"tag:{tag_key}", "Values": ["Databricks"]}]  #Name is a filter type for EC2

    )
 
    instance_ids = []
 
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_ids.append(instance_id)
 
    print(f"Instances with tag '{tag_key}': {instance_ids}")
    if instance_ids:
        # Add the new tag "NoBackup = true" to the identified instances
        ec2_client.create_tags(
            Resources=instance_ids,
            Tags=[{"Key": "NoBackup", "Value": "true"}]
        )
        print(f"Tagged instances: {instance_ids} with NoBackup=true")
    else:
        print(f"No instances found with tag '{tag_key}'.")
 
    return {"statusCode": 200, "body": {"TaggedInstances": instance_ids}}
