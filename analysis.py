# Handling EBS Drift Detection
        elif event_source == "aws.ec2" and event["detail"]["eventName"] in [
            "CreateSnapshot", 
            "DeleteSnapshot", 
            "ModifySnapshotAttribute" ]:
            
            request_parameters = event.get("detail", {}).get("requestParameters", {})
            snapshot_id = request_parameters.get("snapshotId")
            print(f"EBS Volume Modified: {snapshot_id}, By User: {user_email}")
            stack_name = find_stack(snapshot_id, "AWS::EC2::Snapshot")
            resource_name = snapshot_id
