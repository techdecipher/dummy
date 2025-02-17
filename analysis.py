# Handling VPC Drift Detection
elif event_source == "aws.ec2":
    request_parameters = event.get("detail", {}).get("requestParameters", {})
    vpc_id = request_parameters.get("vpcId")

    if not vpc_id:
        print("⚠️ No VPC ID found in event. Skipping.")
        return {"statusCode": 400, "body": "No valid VPC found in event."}

    print(f"🔄 VPC Modified: {vpc_id}, By User: {user_email}")

    stack_name = find_stack(vpc_id, "AWS::EC2::VPC")
    resource_name = vpc_id
