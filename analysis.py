# Handling ELB Drift Detection
elif event_source == "aws.elasticloadbalancing":
    request_parameters = event.get("detail", {}).get("requestParameters", {})
    elb_name = request_parameters.get("loadBalancerName")  # ELB Name

    if not elb_name:
        print("⚠️ No ELB name found in event. Skipping.")
        return {"statusCode": 400, "body": "No valid ELB found in event."}

    print(f"🔄 ELB Modified: {elb_name}, By User: {user_email}")

    stack_name = find_stack(elb_name, "AWS::ElasticLoadBalancing::LoadBalancer")
    resource_name = elb_name
