# Handling EFS Drift Detection
elif event_source == "aws.efs":
    request_parameters = event.get("detail", {}).get("requestParameters", {})
    efs_id = request_parameters.get("fileSystemId")  # EFS File System ID

    if not efs_id:
        print("⚠️ No EFS FileSystem ID found in event. Skipping.")
        return {"statusCode": 400, "body": "No valid EFS FileSystem found in event."}

    print(f"🔄 EFS File System Modified: {efs_id}, By User: {user_email}")

    stack_name = find_stack(efs_id, "AWS::EFS::FileSystem")
    resource_name = efs_id
