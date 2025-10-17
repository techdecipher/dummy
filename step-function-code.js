(function execute(inputs, outputs) {
    gs.log("Custom Action: Starting REST call to AWS Lambda Trigger");

    var restMessage = new sn_ws.RESTMessageV2('AWS Lambda Trigger', 'MPOST');

    // Build the Step Functions execution input directly from Test UI fields
    var stepFunctionInput = {
        lambda1_input: {
            action:                  inputs.action,                 // "add" or "remove"
            RITM_number:            inputs.RITM_number,
            prefix:                 inputs.prefix,
            role:                   inputs.role,
            app_name:               inputs.app_name,
            environment:            inputs.environment,
            product_name:           inputs.product_name,
            project_name:           inputs.project_name,
            members:                inputs.members,                 // keep as string; change to split if needed
            stage:                  inputs.stage,
            RITM_status:            inputs.RITM_status,
            manager_approval_status: inputs.manager_approval_status
        },
        lambda3_input: {
            tbdp_start:               inputs.tbdp_start,
            v_tbdp_date_accomplished: inputs.v_tbdp_date_accomplished,
            v_tbdp_list_database:     inputs.v_tbdp_list_database,
            v_tbdp_environment:       inputs.v_tbdp_environment
        }
    };

    // Wrap for StartExecution
    var payload = {
        stateMachineArn: "arn:aws:states:us-east-1:55555555:stateMachine:tbdp-step-project-pod",
        input: JSON.stringify(stepFunctionInput)
    };

    gs.log("Payload being sent: " + JSON.stringify(payload));

    restMessage.setHeader("Content-Type", "application/json");
    restMessage.setRequestBody(JSON.stringify(payload));

    try {
        var response = restMessage.execute();
        outputs.status = response.getStatusCode();
        outputs.response = response.getBody();
        gs.log("REST call executed. Status: " + outputs.status);
    } catch (ex) {
        outputs.error = ex.message;
        gs.error("REST call failed: " + ex.message);
    }

    gs.log("Custom Action: REST call completed");
})(inputs, outputs);
