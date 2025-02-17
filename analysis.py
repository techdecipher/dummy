# Handling Lambda Drift Detection
elif event_source == "aws.lambda":
    request_parameters = event.get("detail", {}).get("requestParameters", {})
    function_name = request_parameters.get("functionName")

    if not function_name:
        print("⚠️ No Lambda function name found in event. Skipping.")
        return {"statusCode": 400, "body": "No valid Lambda function found in event."}

    print(f"🔄 Lambda Function Modified: {function_name}, By User: {user_email}")

    stack_name = find_stack(function_name, "AWS::Lambda::Function")
    resource_name = function_name
