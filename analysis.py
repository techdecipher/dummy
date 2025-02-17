 try:
        # Start Drift Detection based on the stack name passed to this function
        try:
            response = cloudformation.detect_stack_drift(StackName=stack_name)
            drift_id = response["StackDriftDetectionId"]
            print(f"Started new drift detection for {stack_name}. ID: {drift_id}")
        except cloudformation.exceptions.ClientError as e:
            if "Drift detection is already in progress" in str(e):
                print(f"Drift detection already in progress for {stack_name}. Fetching latest drift status...")
            else:
                print(f"Error starting drift detection: {e}")
                return None

        # Periodically Check Status Until It Completes
        wait_times = [10, 15, 20, 30, 40]  # Retry with increasing wait times
        retries = 0
        max_retries = 10  # Extend retries if the drift detection check process is still taking more

        while retries < max_retries:
            time.sleep(wait_times[min(retries, len(wait_times) - 1)])  # Adaptive wait time
            drift_status = cloudformation.describe_stacks(StackName=stack_name)
            current_status = drift_status["Stacks"][0].get("DriftInformation", {}).get("StackDriftStatus")

            if current_status in ["IN_SYNC", "DRIFTED"]:
                print(f"Drift Check Complete for {stack_name}: {current_status}")
                return current_status

            print(f"Waiting for drift detection to complete... Attempt {retries + 1}/{max_retries}")
            retries += 1

        print(f"Drift check taking too long for {stack_name}")
        return "UNKNOWN"
