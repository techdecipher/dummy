import boto3
import json
import datetime

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    az = 'us-east-1a'
    region = 'us-east-1'
    bucket = 'your-s3-bucket-name'

    # Step 1: Get all running instances in this AZ
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'availability-zone', 'Values': [az]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    # Step 2: Extract unique instance types
    instance_types_set = set()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_types_set.add(instance['InstanceType'])

    results = []

    # Step 3: Check availability for each instance type
    for itype in instance_types_set:
        try:
            ec2.create_capacity_reservation(
                InstanceType=itype,
                InstancePlatform='Linux/UNIX',
                AvailabilityZone=az,
                InstanceCount=1,
                Tenancy='default',
                EbsOptimized=False,
                DryRun=True
            )
        except Exception as e:
            msg = str(e)
            if 'DryRunOperation' in msg:
                results.append({'instance_type': itype, 'status': 'Available'})
            elif 'InsufficientInstanceCapacity' in msg:
                results.append({'instance_type': itype, 'status': 'Unavailable'})
            else:
                results.append({'instance_type': itype, 'status': f'Error: {msg}'})

    # Step 4: Store results to S3
    output = {
        'availability_zone': az,
        'timestamp': str(datetime.datetime.utcnow()),
        'available_capacity': results
    }

    s3.put_object(
        Bucket=bucket,
        Key=f'ec2-capacity-check/{az}-{datetime.datetime.utcnow().isoformat()}.json',
        Body=json.dumps(output)
    )

    return {
        'statusCode': 200,
        'body': 'EC2 capacity check stored in S3.'
    }
