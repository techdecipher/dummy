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
