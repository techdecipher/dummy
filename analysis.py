elif event_name in ["CreateSnapshot", "DeleteSnapshot", "ModifySnapshotAttribute"]:
        request_parameters = event.get("detail", {}).get("requestParameters", {})
        snapshot_id = request_parameters.get("snapshotId")

        if snapshot_id:
            print(f"EBS Snapshot Modified: {snapshot_id}, By User: {user_email}")
            stack_name = find_stack(snapshot_id, "AWS::EC2::Snapshot")
            resource_name = snapshot_id
