Here's a sample AWS Lambda function written in Python that checks the EC2 instance capacity running on a specific Availability Zone (AZ:

```
import boto3

def lambda_handler(event, context):
    # Initialize EC2 client
    ec2 = boto3.client('ec2')

    # Define the Availability Zone (AZ) to check
    az = 'us-west-2a'  # Replace with your desired AZ

    # Get the EC2 instance capacity for the specified AZ
    response = ec2.describe_instance_type_offerings(
        LocationType='availability-zone',
        Filters=[
            {'Name': 'location', 'Values': [az]}
        ]
    )

    # Extract the instance type offerings for the AZ
    instance_type_offerings = response['InstanceTypeOfferings']

    # Initialize a dictionary to store the instance type capacities
    instance_type_capacities = {}

    # Iterate through the instance type offerings
    for offering in instance_type_offerings:
        instance_type = offering['InstanceType']
        response = ec2.describe_instance_type_offering(
            InstanceType=instance_type,
            LocationType='availability-zone',
            Filters=[
                {'Name': 'location', 'Values': [az]}
            ]
        )
        instance_type_capacities[instance_type] = response['InstanceTypeOfferingSet'][0]['OfferingClass']

    # Print the instance type capacities for the AZ
    print(f'Instance type capacities for AZ {az}:')
    for instance_type, capacity in instance_type_capacities.items():
        print(f'{instance_type}: {capacity}')

    return {
        'statusCode': 200,
        'body': instance_type_capacities
    }
```

This Lambda function:

1. Initializes an EC2 client using the `boto3` library.
2. Defines the Availability Zone (AZ) to check.
3. Uses the `describe_instance_type_offerings` method to get the EC2 instance type offerings for the specified AZ.
4. Extracts the instance type offerings for the AZ.
5. Initializes a dictionary to store the instance type capacities.
6. Iterates through the instance type offerings and uses the `describe_instance_type_offering` method to get the instance type capacity for each offering.
7. Stores the instance type capacities in the dictionary.
8. Prints the instance type capacities for the AZ.
9. Returns the instance type capacities as a JSON response.

To deploy this Lambda function:

1. Create a new Lambda function in the AWS Management Console.
2. Choose Python as the runtime.
3. Upload the code as a ZIP file or copy-paste it into the inline editor.
4. Set the handler to `index.lambda_handler`.
5. Configure the environment variables and IAM role as needed.
6. Test the function using the AWS Lambda console or AWS CLI.

Note: This code assumes you have the necessary IAM permissions to access EC2 resources. Make sure to update the AZ variable to match your desired Availability Zone.
