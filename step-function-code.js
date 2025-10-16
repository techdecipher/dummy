{
  "Comment": "Invoke three Lambdas with minimal, isolated payloads",
  "StartAt": "Invoke_azure_Lambda",
  "States": {
    "Invoke_azure_Lambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:5555555555:function:tbdp-test-lambda",
        "Payload": {
          "action.$": "$.lambda1_input.action"
        }
      },
      "OutputPath": "$.Payload",
      "Next": "Invoke_git_Lambda"
    },

    "Invoke_git_Lambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:5555555555:function:github_lambda",
        "Payload": {}                           // <-- send nothing
      },
      "OutputPath": "$.Payload",                // <-- only pass Lambda 2's response
      "Next": "Invoke_servicenow_lambda"
    },

    "Invoke_servicenow_lambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:5555555555:function:ServiceNow_lambda:$LATEST",
        "Payload": {
          "body.$": "States.JsonToString($.lambda3_input)"  
          /* If you update Lambda 3 to accept plain keys instead of body:
             replace with:
             "tbdp_start.$": "$.lambda3_input.tbdp_start",
             "v_tbdp_date_accomplished.$": "$.lambda3_input.v_tbdp_date_accomplished",
             "v_tbdp_list_database.$": "$.lambda3_input.v_tbdp_list_database",
             "v_tbdp_environment.$": "$.lambda3_input.v_tbdp_environment"
          */
        }
      },
      "OutputPath": "$.Payload",
      "End": true
    }
  }
}
