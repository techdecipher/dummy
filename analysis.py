# Handling Secrets Manager Drift Detection
elif event_source == "aws.secretsmanager":
    request_parameters = event.get("detail", {}).get("requestParameters", {})
    secret_arn = request_parameters.get("secretId")  # ARN of the modified secret

    if not secret_arn:
        print("⚠️ No Secrets Manager ARN found in event. Skipping.")
        return {"statusCode": 400, "body": "No valid Secrets Manager ARN found in event."}

    secret_name = secret_arn.split(":")[-1]  # Extracting secret name
    print(f"🔄 Secrets Manager Secret Modified: {secret_name}, By User: {user_email}")

    stack_name = find_stack(secret_name, "AWS::SecretsManager::Secret")
    resource_name = secret_name
