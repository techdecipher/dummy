import boto3
import json
import datetime

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    az = 'us-east-1a'  # Replace with your target AZ
    region = 'us-east-1'
    bucket = 'your-s3-bucket-name'  # Replace with your S3 bucket
    instance_types = ['t3.micro', 't3.small', 't3.medium']  # Add more as needed
    results = []

    for itype in instance_types:
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
