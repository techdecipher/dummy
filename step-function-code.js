{
  "Comment": "A simple Step Function to invoke Lambda",
  "StartAt": "Invoke_azure_Lambda",
  "States": {
    "Invoke_azure_Lambda": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:5555555555:function:tbdp-test-lambda",
      "ResultPath": "$.lambdaResult",
      "Parameters": {
        "action.$": "$.lambda1_input.action"
      },
      "Next": "Invoke_git_Lambda"
    },
    "Invoke_git_Lambda": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:5555555555:function:github_lambda",
      "InputPath": "$",
      "ResultPath": "$.lambdaResult",
      "Next": "Invoke_servicenow_lambda"
    },
    "Invoke_servicenow_lambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:5555555555:function:ServiceNow_lambda:$LATEST",
        "Payload": {
          "tbdp_start.$": "$.lambda3_input.tbdp_start",
          "v_tbdp_date_accomplished.$": "$.lambda3_input.v_tbdp_date_accomplished",
          "v_tbdp_list_database.$": "$.lambda3_input.v_tbdp_list_database",
          "v_tbdp_environment.$": "$.lambda3_input.v_tbdp_environment"
        }
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "End": true
    }
  }
}


(function execute(inputs, outputs) {
    gs.log("Custom Action: Starting REST call to AWS Lambda Trigger");

    var restMessage = new sn_ws.RESTMessageV2('AWS Lambda Trigger', 'MPOST');

    // Build the actual input payload
    var stepFunctionInput = {
        lambda1_input: {
            action: "remove"
        },
        lambda3_input: {
            tbdp_start: "Analysis",
            v_tbdp_date_accomplished: "2025-10-13 11:42:46 AM",
            v_tbdp_list_database: "NA",
            v_tbdp_environment: "Dev"
        }
    };

    // Wrap it in the required structure for StartExecution API
    var payload = {
        stateMachineArn: "arn:aws:states:us-east-1:5555555555:stateMachine:name-of-arn",
        input: JSON.stringify(stepFunctionInput) 
    };

    gs.log("Payload being sent: " + JSON.stringify(payload));

    restMessage.setRequestBody(JSON.stringify(payload));
    restMessage.setHeader("Content-Type", "application/json");

    try {
        var response = restMessage.execute();
        var responseBody = response.getBody();
        var httpStatus = response.getStatusCode();

        gs.log("REST call executed. Status: " + httpStatus);
        gs.log("Response body: " + responseBody);

        outputs.response = responseBody;
        outputs.status = httpStatus;
    } catch (ex) {
        gs.error("REST call failed: " + ex.message);
        outputs.error = ex.message;
    }

    gs.log("Custom Action: REST call completed");
})(inputs, outputs);

{
  "lambda1_input": {
    "action": "remove"
  },
  "lambda3_input": {
    "tbdp_start": "Analysis",
    "v_tbdp_date_accomplished": "2025-10-13 11:42:46 AM",
    "v_tbdp_list_database": "NA",
    "v_tbdp_environment": "Dev"
  }
}


{
  "body": "{\n  \"tbdp_start\": \"Analysis\",\n  \"v_tbdp_date_accomplished\": \"2025-09-25 11:42:46 AM\",\n  \"v_tbdp_list_database\": \"NA\",\n  \"v_tbdp_environment\": \"Dev\"\n}"
}

