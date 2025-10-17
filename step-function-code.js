An error occurred while executing the state 'Invoke_azure_Lambda' (entered at the event id #7). The JSONPath '$.lambda1_input.action' specified for the field 'action.$' could not be found in the input '{"lambda1_input":{},"lambda3_input":{}}'


2025-10-17 12:58:23InformationSTATEMENT BATCHER DEBUG: Committing 1/1 [BatchStatement: 3 statement(s)]
2025-10-17 12:58:23InformationSTATEMENT BATCHER DEBUG: Committing batch of 3
2025-10-17 12:58:23WarningEncountered undeclared output variable: response
2025-10-17 12:58:23WarningEncountered undeclared output variable: status
2025-10-17 12:58:23Information*** Script: Custom Action: REST call completed
2025-10-17 12:58:23Information*** Script: REST call executed. Status: 200
2025-10-17 12:58:22Information[0:00:00.219] id: tmnatest_1[glide.10 (connpid=346126)] for: DBQuery#loadResultSet[sys_hub_action_type_definition: ORDERBYsys_id]
2025-10-17 12:58:21WarningNo URIs provided, removing all URI matcher rules
2025-10-17 12:58:21Information*** Script: Payload being sent: {"stateMachineArn":"arn:aws:states:us-east-1:555555555:stateMachine:tbdp-step-project-pod","input":"{\"lambda1_input\":{},\"lambda3_input\":{}}"}
2025-10-17 12:58:21Information*** Script: Custom Action: Starting REST call to AWS Lambda Trigger
has context menu

