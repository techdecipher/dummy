2025-02-14T11:44:07.968Z
INIT_START Runtime Version: python:3.11.v46 Runtime Version ARN: arn:aws:lambda:us-east-1::runtime:84bc5fe9641102b252ebbfd80d16f2791f7bcca59e26ce68d95066317adf4503
2025-02-14T11:44:08.444Z
START RequestId: 05f00d4f-b550-4fe7-9fa0-6e79db2613bb Version: $LATEST
2025-02-14T11:44:08.444Z
🔹 Received event: {
2025-02-14T11:44:08.444Z
"version": "0",
2025-02-14T11:44:08.444Z
"id": "79dd10e5-77e5-bc3a-042f-04c5500015f7",
2025-02-14T11:44:08.444Z
"detail-type": "AWS API Call via CloudTrail",
2025-02-14T11:44:08.444Z
"source": "aws.sqs",
2025-02-14T11:44:08.444Z
"account": "158366596870",
2025-02-14T11:44:08.444Z
"time": "2025-02-14T11:43:47Z",
2025-02-14T11:44:08.444Z
"region": "us-east-1",
2025-02-14T11:44:08.444Z
"resources": [],
2025-02-14T11:44:08.444Z
"detail": {
2025-02-14T11:44:08.444Z
"eventVersion": "1.10",
2025-02-14T11:44:08.444Z
"userIdentity": {
2025-02-14T11:44:08.444Z
"type": "AssumedRole",
2025-02-14T11:44:08.444Z
"principalId": "AROASJX3CP4DAYSSJTE4:503430218",
2025-02-14T11:44:08.444Z
"arn": "arn:aws:sts::158366596870:assumed-role/bu-ge-dna-cldmgmt-fed/503430218",
2025-02-14T11:44:08.444Z
"accountId": "158366596870",
2025-02-14T11:44:08.444Z
"accessKeyId": "ASIASJX3CP4DETDQSDC4",
2025-02-14T11:44:08.444Z
"sessionContext": {
2025-02-14T11:44:08.444Z
"sessionIssuer": {
2025-02-14T11:44:08.444Z
"type": "Role",
2025-02-14T11:44:08.444Z
"principalId": "AROASJX3CP4DAYSSJTE4",
2025-02-14T11:44:08.444Z
"arn": "arn:aws:iam::158366596870:role/bu-ge-dna-cldmgmt-fed",
2025-02-14T11:44:08.444Z
"accountId": "158366596870",
2025-02-14T11:44:08.444Z
"userName": "bu-ge-dna-cldmgmt-fed"
2025-02-14T11:44:08.444Z
},
2025-02-14T11:44:08.444Z
"attributes": {
2025-02-14T11:44:08.444Z
"creationDate": "2025-02-14T11:19:30Z",
2025-02-14T11:44:08.444Z
"mfaAuthenticated": "false"
2025-02-14T11:44:08.444Z
}
2025-02-14T11:44:08.444Z
}
2025-02-14T11:44:08.444Z
},
2025-02-14T11:44:08.444Z
"eventTime": "2025-02-14T11:43:47Z",
2025-02-14T11:44:08.444Z
"eventSource": "sqs.amazonaws.com",
2025-02-14T11:44:08.444Z
"eventName": "SetQueueAttributes",
2025-02-14T11:44:08.444Z
"awsRegion": "us-east-1",
2025-02-14T11:44:08.444Z
"sourceIPAddress": "165.156.28.92",
2025-02-14T11:44:08.444Z
"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
2025-02-14T11:44:08.444Z
"requestParameters": {
2025-02-14T11:44:08.444Z
"queueUrl": "https://sqs.us-east-1.amazonaws.com/158366596870/drift-test-queue-12-158366596870-us-east-1",
2025-02-14T11:44:08.444Z
"attributes": {
2025-02-14T11:44:08.444Z
"Policy": "",
2025-02-14T11:44:08.444Z
"ReceiveMessageWaitTimeSeconds": "0",
2025-02-14T11:44:08.444Z
"SqsManagedSseEnabled": "true",
2025-02-14T11:44:08.444Z
"DelaySeconds": "0",
2025-02-14T11:44:08.444Z
"KmsMasterKeyId": "",
2025-02-14T11:44:08.444Z
"RedrivePolicy": "",
2025-02-14T11:44:08.444Z
"MessageRetentionPeriod": "345600",
2025-02-14T11:44:08.444Z
"MaximumMessageSize": "262144",
2025-02-14T11:44:08.444Z
"VisibilityTimeout": "32",
2025-02-14T11:44:08.444Z
"RedriveAllowPolicy": ""
2025-02-14T11:44:08.444Z
}
2025-02-14T11:44:08.444Z
},
2025-02-14T11:44:08.444Z
"responseElements": null,
2025-02-14T11:44:08.444Z
"requestID": "692361d5-1a05-5ca9-bbd8-01fc34b6aef4",
2025-02-14T11:44:08.444Z
"eventID": "97d05f9f-bf45-49af-a9db-eb1c7ff0c4b5",
2025-02-14T11:44:08.444Z
"readOnly": false,
2025-02-14T11:44:08.444Z
"resources": [
2025-02-14T11:44:08.444Z
{
2025-02-14T11:44:08.444Z
"accountId": "158366596870",
2025-02-14T11:44:08.444Z
"type": "AWS::SQS::Queue",
2025-02-14T11:44:08.444Z
"ARN": "arn:aws:sqs:us-east-1:158366596870:drift-test-queue-12-158366596870-us-east-1"
2025-02-14T11:44:08.444Z
}
2025-02-14T11:44:08.444Z
],
2025-02-14T11:44:08.444Z
"eventType": "AwsApiCall",
2025-02-14T11:44:08.444Z
"managementEvent": true,
2025-02-14T11:44:08.444Z
"recipientAccountId": "158366596870",
2025-02-14T11:44:08.444Z
"eventCategory": "Management",
2025-02-14T11:44:08.444Z
"tlsDetails": {
2025-02-14T11:44:08.444Z
"tlsVersion": "TLSv1.3",
2025-02-14T11:44:08.444Z
"cipherSuite": "TLS_AES_128_GCM_SHA256",
2025-02-14T11:44:08.444Z
"clientProvidedHostHeader": "sqs.us-east-1.amazonaws.com"
2025-02-14T11:44:08.444Z
},
2025-02-14T11:44:08.444Z
"sessionCredentialFromConsole": "true"
2025-02-14T11:44:08.444Z
}
2025-02-14T11:44:08.444Z
}
2025-02-14T11:44:08.444Z
🔄 SQS Queue Modified: drift-test-queue-12-158366596870-us-east-1, By User: unknown@ge.com
2025-02-14T11:44:08.857Z
✅ SQS Queue drift-test-queue-12-158366596870-us-east-1 belongs to stack SQS-stack-checking-for-drift
2025-02-14T11:44:19.044Z
✅ Drift Check Complete for SQS-stack-checking-for-drift: DRIFTED
2025-02-14T11:44:19.044Z
🚨 Drift detected! User responsible: unknown@ge.com
2025-02-14T11:44:19.221Z
✅ SES Notification Sent to unknown@ge.com! Message ID: 0100019504461eb5-06b8fb08-2453-422c-8798-3c1548fbf626-000000
2025-02-14T11:44:19.224Z
END RequestId: 05f00d4f-b550-4fe7-9fa0-6e79db2613bb
