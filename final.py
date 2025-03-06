  # Handle EC2 Drift Detection
        elif event_source == "aws.ec2" and event["detail"]["eventName"] in [
            "ModifyInstanceAttribute",
            "StartInstances",
            "StopInstances",
            "RebootInstances",
            "TerminateInstances" ]:
           
            request_parameters = event.get("detail", {}).get("requestParameters", {})
            resource_items = request_parameters.get("resourcesSet", {}).get("items", [])
            instance_id = resource_items[0].get("resourceId") if resource_items else None
            if not instance_id:
                print("No EC2 instance ID found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid EC2 instance found in event."}
            
            print(f"EC2 Instance Modified: {instance_id}, By User: {user_email}")
            
            stack_name = find_stack(instance_id, "AWS::EC2::Instance")
            resource_name = instance_id
            event_type = "EC2 Instance"
