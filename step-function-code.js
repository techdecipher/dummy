{
  "lambda1_input": {
    "action": "add",
    "RITM_number": "RITM12349999",
    "prefix": "tbdp",
    "role": "Data Analyst",
    "app_name": "persona",
    "environment": "dev",
    "product_name": "analyst",
    "project_name": "NA",
    "members": "sourav.jaish.kumar@sbs.com",
    "stage": "dev",
    "RITM_status": "IN Process",
    "manager_approval_status": "Pending"
  },
  "lambda3_input": {
    "tbdp_start": "Analysis",
    "v_tbdp_date_accomplished": "2025-10-16 11:42:46 AM",
    "v_tbdp_list_database": "NA",
    "v_tbdp_environment": "Dev"
  }
}


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
        stateMachineArn: "arn:aws:states:us-east-1:55555555:stateMachine:tbdp-step-project-pod",
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


