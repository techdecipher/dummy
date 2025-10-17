2025-10-17 15:06:27
Information
STATEMENT BATCHER DEBUG: Committing 1/1 [BatchStatement: 3 statement(s)]
2025-10-17 15:06:27
Information
STATEMENT BATCHER DEBUG: Committing batch of 3
2025-10-17 15:06:27
Error
Encountered error executing instruction: ActionErrorEvalInstruction{id=3, conditions=[], statusKey=rooto.__action_status__, dontTreatAsErrorKey=rooto.__dont_treat_as_error__}, errorMessage:Error: missing ( before function parameters. (Process Automation.3c653bcf1ba8ba506cdcc998624bcbe1; line 11), errorCode:1
2025-10-17 15:06:27
Error
Encountered error executing instruction: OpInstruction{id=1, opClass=com.snc.process_flow.operation.script.ScriptOperation, io=ReadOnlyDefaultOutputsIo{input={mid_selection=StringValue{fValue='auto_select'}, capabilities=StringValue{fValue=''}, connection_alias=StringValue{fValue=''}, application=StringValue{fValue='35aa573fd7802200bdbaee5b5e610375'}, mid_server=StringValue{fValue=''}, mid_cluster...
2025-10-17 15:06:27
Warning
Javascript compiler exception: missing ( before function parameters. (Process Automation.3c653bcf1ba8ba506cdcc998624bcbe1; line 11) in:
(function execute(inputs, outputs) {
    gs.log("Custom Action: Starting REST call to AWS Lambda Trigger");

    var restMessage = new sn_ws.RESTMessageV2('AWS Lambda Trigger', 'MPOST');

    // Build the actual input payload
    var stepFunctionInput = {
 ...
2025-10-17 15:06:27
Warning
Script compilation error: Script Identifier: Process Automation.3c653bcf1ba8ba506cdcc998624bcbe1, Error Description: missing ( before function parameters. (Process Automation.3c653bcf1ba8ba506cdcc998624bcbe1; line 11), Script ES Level: 0, Interpreted Mode: true
