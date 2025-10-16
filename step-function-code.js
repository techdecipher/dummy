{
  "StartAt": "Invoke_azure_Lambda",
  "States": {
    "Invoke_azure_Lambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:5555555555:function:tbdp-test-lambda",
        "Payload": { "action.$": "$.lambda1_input.action" }
      },
      "ResultPath": "$.azureResult",     // attach result here
      "Next": "Invoke_git_Lambda"
    },

    "Invoke_git_Lambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:5555555555:function:github_lambda",
        "Payload": {}                     // no input
      },
      "ResultPath": "$.gitResult",        // attach here, keep root intact
      "Next": "Invoke_servicenow_lambda"
    },

    "Invoke_servicenow_lambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",

      "InputPath": "$.lambda3_input",     // show only lambda3_input to this state

      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:5555555555:function:ServiceNow_lambda:$LATEST",
        "Payload": {
          "body.$": "States.JsonToString($)"   // matches your Lambda-3 test (event.body string)
        }
      },
      "OutputPath": "$.Payload",
      "End": true
    }
  }
}
