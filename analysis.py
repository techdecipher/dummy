# Handling EBS Drift Detection (Both Snapshots and Volumes)
elif event_source == "aws.ec2" and event["detail"]["eventName"] in [
    "CreateSnapshot", 
    "DeleteSnapshot", 
    "ModifySnapshotAttribute",
    "ModifyVolume",
    "AttachVolume",
    "DetachVolume",
    "CreateVolume",
    "DeleteVolume"
]:
    request_parameters = event.get("detail", {}).get("requestParameters", {})
    
    # Handle Snapshots
    if "snapshotId" in request_parameters:
        resource_id = request_parameters.get("snapshotId")
        resource_type = "AWS::EC2::Snapshot"
    
    # Handle Volumes
    elif "volumeId" in request_parameters:
        resource_id = request_parameters.get("volumeId")
        resource_type = "AWS::EC2::Volume"

    else:
        print("⚠️ No EBS Volume or Snapshot found in event. Skipping.")
        return {"statusCode": 400, "body": "No valid EBS resource found in event."}

    print(f"EBS Resource Modified: {resource_id}, By User: {user_email}")
    
    stack_name = find_stack(resource_id, resource_type)
    resource_name = resource_id
