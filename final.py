2025-03-06T09:58:11.342Z
"attributes": {
2025-03-06T09:58:11.342Z
"creationDate": "2025-03-06T09:27:55Z",
2025-03-06T09:58:11.342Z
"mfaAuthenticated": "false"
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
},
2025-03-06T09:58:11.342Z
"eventTime": "2025-03-06T09:58:07Z",
2025-03-06T09:58:11.342Z
"eventSource": "ec2.amazonaws.com",
2025-03-06T09:58:11.342Z
"eventName": "TerminateInstances",
2025-03-06T09:58:11.342Z
"awsRegion": "us-east-1",
2025-03-06T09:58:11.342Z
"sourceIPAddress": "100.28.222.195",
2025-03-06T09:58:11.342Z
"userAgent": "Boto3/1.34.145 md/Botocore#1.34.145 ua/2.0 os/linux#5.10.233-244.887.amzn2.x86_64 md/arch#x86_64 lang/python#3.11.10 md/pyimpl#CPython exec-env/AWS_Lambda_python3.11 cfg/retry-mode#legacy Botocore/1.34.145",
2025-03-06T09:58:11.342Z
"requestParameters": {
2025-03-06T09:58:11.342Z
"instancesSet": {
2025-03-06T09:58:11.342Z
"items": [
2025-03-06T09:58:11.342Z
{
2025-03-06T09:58:11.342Z
"instanceId": "i-04b588def92013bef"
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
]
2025-03-06T09:58:11.342Z
},
2025-03-06T09:58:11.342Z
"force": false,
2025-03-06T09:58:11.342Z
"skipOsShutdown": false
2025-03-06T09:58:11.342Z
},
2025-03-06T09:58:11.342Z
"responseElements": {
2025-03-06T09:58:11.342Z
"requestId": "95475d9a-882c-4176-902f-b5ad926bc44b",
2025-03-06T09:58:11.342Z
"instancesSet": {
2025-03-06T09:58:11.342Z
"items": [
2025-03-06T09:58:11.342Z
{
2025-03-06T09:58:11.342Z
"instanceId": "i-04b588def92013bef",
2025-03-06T09:58:11.342Z
"currentState": {
2025-03-06T09:58:11.342Z
"code": 32,
2025-03-06T09:58:11.342Z
"name": "shutting-down"
2025-03-06T09:58:11.342Z
},
2025-03-06T09:58:11.342Z
"previousState": {
2025-03-06T09:58:11.342Z
"code": 16,
2025-03-06T09:58:11.342Z
"name": "running"
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
]
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
},
2025-03-06T09:58:11.342Z
"requestID": "95475d9a-882c-4176-902f-b5ad926bc44b",
2025-03-06T09:58:11.342Z
"eventID": "eda2b48e-9c50-427c-bcc3-54c42327100b",
2025-03-06T09:58:11.342Z
"readOnly": false,
2025-03-06T09:58:11.342Z
"eventType": "AwsApiCall",
2025-03-06T09:58:11.342Z
"managementEvent": true,
2025-03-06T09:58:11.342Z
"recipientAccountId": "753920291680",
2025-03-06T09:58:11.342Z
"eventCategory": "Management",
2025-03-06T09:58:11.342Z
"tlsDetails": {
2025-03-06T09:58:11.342Z
"tlsVersion": "TLSv1.3",
2025-03-06T09:58:11.342Z
"cipherSuite": "TLS_AES_128_GCM_SHA256",
2025-03-06T09:58:11.342Z
"clientProvidedHostHeader": "ec2.us-east-1.amazonaws.com"
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
}
2025-03-06T09:58:11.342Z
No EC2 instance ID found in event. Skipping.
2025-03-06T09:58:11.343Z
END RequestId: dc807521-83c6-439d-b6b0-cd76ea0cc12f
2025-03-06T09:58:11.343Z
REPORT RequestId: dc807521-83c6-439d-b6b0-cd76ea0cc12f Duration: 1.55 ms Billed Duration: 2 ms Memory Size: 512 MB Max Memory Used: 88 MB
2025-03-06T09:58:13.134Z
START RequestId: 9a347e67-8e77-4744-87b9-2f05cb9a62d8 Version: $LATEST
2025-03-06T09:58:13.134Z
Received event: {
2025-03-06T09:58:13.134Z
"version": "0",
2025-03-06T09:58:13.134Z
"id": "da14712a-d363-e8de-f05a-32c067bcb0df",
2025-03-06T09:58:13.134Z
"detail-type": "AWS API Call via CloudTrail",
2025-03-06T09:58:13.134Z
"source": "aws.ec2",
2025-03-06T09:58:13.134Z
"account": "753920291680",
2025-03-06T09:58:13.134Z
"time": "2025-03-06T09:58:08Z",
2025-03-06T09:58:13.134Z
"region": "us-east-1",
2025-03-06T09:58:13.134Z
"resources": [],
2025-03-06T09:58:13.134Z
"detail": {
2025-03-06T09:58:13.134Z
"eventVersion": "1.10",
2025-03-06T09:58:13.134Z
"userIdentity": {
2025-03-06T09:58:13.134Z
"type": "AssumedRole",
2025-03-06T09:58:13.134Z
"principalId": "AROAIBY7OLUDPY6JZWQTM:sam-OpsGuardian-EC2",
2025-03-06T09:58:13.134Z
"arn": "arn:aws:sts::753920291680:assumed-role/bu-pw-lambda-cloudops/sam-OpsGuardian-EC2",
2025-03-06T09:58:13.134Z
"accountId": "753920291680",
2025-03-06T09:58:13.134Z
"accessKeyId": "ASIA27CJGWNQHFDWCKDR",
2025-03-06T09:58:13.134Z
"sessionContext": {
2025-03-06T09:58:13.134Z
"sessionIssuer": {
2025-03-06T09:58:13.134Z
"type": "Role",
2025-03-06T09:58:13.134Z
"principalId": "AROAIBY7OLUDPY6JZWQTM",
2025-03-06T09:58:13.134Z
"arn": "arn:aws:iam::753920291680:role/hq/bu-pw-lambda-cloudops",
2025-03-06T09:58:13.134Z
"accountId": "753920291680",
2025-03-06T09:58:13.134Z
"userName": "bu-pw-lambda-cloudops"
2025-03-06T09:58:13.134Z
},
2025-03-06T09:58:13.134Z
"attributes": {
2025-03-06T09:58:13.134Z
"creationDate": "2025-03-06T08:54:55Z",
2025-03-06T09:58:13.134Z
"mfaAuthenticated": "false"
2025-03-06T09:58:13.134Z
}
2025-03-06T09:58:13.134Z
}
2025-03-06T09:58:13.134Z
},
2025-03-06T09:58:13.134Z
"eventTime": "2025-03-06T09:58:08Z",
2025-03-06T09:58:13.134Z
"eventSource": "ec2.amazonaws.com",
2025-03-06T09:58:13.134Z
"eventName": "ModifyInstanceAttribute",
2025-03-06T09:58:13.134Z
"awsRegion": "us-east-1",
2025-03-06T09:58:13.134Z
"sourceIPAddress": "3.237.66.170",
2025-03-06T09:58:13.134Z
"userAgent": "Boto3/1.34.145 md/Botocore#1.34.145 ua/2.0 os/linux#5.10.233-244.887.amzn2.x86_64 md/arch#x86_64 lang/python#3.11.10 md/pyimpl#CPython exec-env/AWS_Lambda_python3.11 cfg/retry-mode#legacy Botocore/1.34.145",
2025-03-06T09:58:13.134Z
"requestParameters": {
2025-03-06T09:58:13.134Z
"instanceId": "i-031c2cfcd064f128f",
2025-03-06T09:58:13.134Z
"attribute": "disableApiTermination",
2025-03-06T09:58:13.134Z
"value": "<sensitiveDataRemoved>"
2025-03-06T09:58:13.134Z
},
2025-03-06T09:58:13.134Z
"responseElements": {
2025-03-06T09:58:13.134Z
"requestId": "59a79277-2b02-4ae0-a39f-d39c8ab508e0",
2025-03-06T09:58:13.134Z
"_return": true
2025-03-06T09:58:13.134Z
},
2025-03-06T09:58:13.134Z
"requestID": "59a79277-2b02-4ae0-a39f-d39c8ab508e0",
2025-03-06T09:58:13.134Z
"eventID": "6eaf994a-87d2-4b8a-a688-be5fb4b3e3cf",
2025-03-06T09:58:13.134Z
"readOnly": false,
2025-03-06T09:58:13.134Z
"eventType": "AwsApiCall",
2025-03-06T09:58:13.134Z
"managementEvent": true,
2025-03-06T09:58:13.134Z
"recipientAccountId": "753920291680",
2025-03-06T09:58:13.134Z
"eventCategory": "Management",
2025-03-06T09:58:13.134Z
"tlsDetails": {
2025-03-06T09:58:13.134Z
"tlsVersion": "TLSv1.3",
2025-03-06T09:58:13.134Z
"cipherSuite": "TLS_AES_128_GCM_SHA256",
2025-03-06T09:58:13.134Z
"clientProvidedHostHeader": "ec2.us-east-1.amazonaws.com"
2025-03-06T09:58:13.134Z
}
2025-03-06T09:58:13.134Z
}
2025-03-06T09:58:13.134Z
}
2025-03-06T09:58:13.134Z
No EC2 instance ID found in event. Skipping.
2025-03-06T09:58:13.135Z
END RequestId: 9a347e67-8e77-4744-87b9-2f05cb9a62d8
2025-03-06T09:58:13.135Z
REPORT RequestId: 9a347e67-8e77-4744-87b9-2f05cb9a62d8 Duration: 1.34 ms Billed Duration: 2 ms Memory Size: 512 MB Max Memory Used: 88 MB
2025-03-06T09:58:22.084Z
START RequestId: 6d96e229-8190-405a-a8a0-2c43422c3fdb Version: $LATEST
2025-03-06T09:58:22.085Z
Received event: {
2025-03-06T09:58:22.085Z
"version": "0",
2025-03-06T09:58:22.085Z
"id": "d1f1a049-09c6-e05d-b535-3e84a1251158",
2025-03-06T09:58:22.085Z
"detail-type": "AWS API Call via CloudTrail",
2025-03-06T09:58:22.085Z
"source": "aws.ec2",
2025-03-06T09:58:22.085Z
"account": "753920291680",
2025-03-06T09:58:22.085Z
"time": "2025-03-06T09:58:18Z",
2025-03-06T09:58:22.085Z
"region": "us-east-1",
2025-03-06T09:58:22.085Z
"resources": [],
2025-03-06T09:58:22.085Z
"detail": {
2025-03-06T09:58:22.085Z
"eventVersion": "1.10",
2025-03-06T09:58:22.085Z
"userIdentity": {
2025-03-06T09:58:22.085Z
"type": "AssumedRole",
2025-03-06T09:58:22.085Z
"principalId": "AROAIBY7OLUDPY6JZWQTM:sam-OpsGuardian-EC2",
2025-03-06T09:58:22.085Z
"arn": "arn:aws:sts::753920291680:assumed-role/bu-pw-lambda-cloudops/sam-OpsGuardian-EC2",
2025-03-06T09:58:22.085Z
"accountId": "753920291680",
2025-03-06T09:58:22.085Z
"accessKeyId": "ASIA27CJGWNQNWM34HE4",
2025-03-06T09:58:22.085Z
"sessionContext": {
2025-03-06T09:58:22.085Z
"sessionIssuer": {
2025-03-06T09:58:22.085Z
"type": "Role",
2025-03-06T09:58:22.085Z
"principalId": "AROAIBY7OLUDPY6JZWQTM",
2025-03-06T09:58:22.085Z
"arn": "arn:aws:iam::753920291680:role/hq/bu-pw-lambda-cloudops",
2025-03-06T09:58:22.085Z
"accountId": "753920291680",
2025-03-06T09:58:22.085Z
"userName": "bu-pw-lambda-cloudops"
2025-03-06T09:58:22.085Z
},
2025-03-06T09:58:22.085Z
"attributes": {
2025-03-06T09:58:22.085Z
"creationDate": "2025-03-06T09:48:52Z",
2025-03-06T09:58:22.085Z
"mfaAuthenticated": "false"
2025-03-06T09:58:22.085Z
}
2025-03-06T09:58:22.085Z
}
2025-03-06T09:58:22.085Z
},
2025-03-06T09:58:22.085Z
"eventTime": "2025-03-06T09:58:18Z",
2025-03-06T09:58:22.085Z
"eventSource": "ec2.amazonaws.com",
2025-03-06T09:58:22.085Z
"eventName": "ModifyInstanceAttribute",
2025-03-06T09:58:22.085Z
"awsRegion": "us-east-1",
2025-03-06T09:58:22.085Z
"sourceIPAddress": "54.158.64.105",
2025-03-06T09:58:22.085Z
"userAgent": "Boto3/1.34.145 md/Botocore#1.34.145 ua/2.0 os/linux#5.10.233-244.887.amzn2.x86_64 md/arch#x86_64 lang/python#3.11.10 md/pyimpl#CPython exec-env/AWS_Lambda_python3.11 cfg/retry-mode#legacy Botocore/1.34.145",
2025-03-06T09:58:22.085Z
"requestParameters": {
2025-03-06T09:58:22.085Z
"instanceId": "i-0a7e364ba3c7ef180",
2025-03-06T09:58:22.085Z
"attribute": "disableApiTermination",
2025-03-06T09:58:22.085Z
"value": "<sensitiveDataRemoved>"
2025-03-06T09:58:22.085Z
},
2025-03-06T09:58:22.085Z
"responseElements": {
2025-03-06T09:58:22.085Z
"requestId": "756a9e0a-3c39-4672-ba07-282b81609fbf",
2025-03-06T09:58:22.085Z
"_return": true
2025-03-06T09:58:22.085Z
},
2025-03-06T09:58:22.085Z
"requestID": "756a9e0a-3c39-4672-ba07-282b81609fbf",
2025-03-06T09:58:22.085Z
"eventID": "14ab447c-10b4-430d-bf81-9752c00a1394",
2025-03-06T09:58:22.085Z
"readOnly": false,
2025-03-06T09:58:22.085Z
"eventType": "AwsApiCall",
2025-03-06T09:58:22.085Z
"managementEvent": true,
2025-03-06T09:58:22.085Z
"recipientAccountId": "753920291680",
2025-03-06T09:58:22.085Z
"eventCategory": "Management",
2025-03-06T09:58:22.085Z
"tlsDetails": {
2025-03-06T09:58:22.085Z
"tlsVersion": "TLSv1.3",
2025-03-06T09:58:22.085Z
"cipherSuite": "TLS_AES_128_GCM_SHA256",
2025-03-06T09:58:22.085Z
"clientProvidedHostHeader": "ec2.us-east-1.amazonaws.com"
2025-03-06T09:58:22.085Z
}
2025-03-06T09:58:22.085Z
}
2025-03-06T09:58:22.085Z
}
2025-03-06T09:58:22.085Z
No EC2 instance ID found in event. Skipping.
2025-03-06T09:58:22.086Z
END RequestId: 6d96e229-8190-405a-a8a0-2c43422c3fdb
2025-03-06T09:58:22.086Z
REPORT RequestId: 6d96e229-8190-405a-a8a0-2c43422c3fdb Duration: 1.59 ms Billed Duration: 2 ms Memory Size: 512 MB Max Memory Used: 88 MB
2025-03-06T09:58:22.146Z
START RequestId: 671d319a-031d-4866-963e-1e8367e12326 Version: $LATEST
2025-03-06T09:58:22.147Z
Received event: {
2025-03-06T09:58:22.147Z
"version": "0",
2025-03-06T09:58:22.147Z
"id": "8ed23c2f-2651-b091-a0e4-5682fdc8b123",
2025-03-06T09:58:22.147Z
"detail-type": "AWS API Call via CloudTrail",
2025-03-06T09:58:22.147Z
"source": "aws.ec2",
2025-03-06T09:58:22.147Z
"account": "753920291680",
2025-03-06T09:58:22.147Z
"time": "2025-03-06T09:58:18Z",
2025-03-06T09:58:22.147Z
"region": "us-east-1",
2025-03-06T09:58:22.147Z
"resources": [],
2025-03-06T09:58:22.147Z
"detail": {
2025-03-06T09:58:22.147Z
"eventVersion": "1.10",
2025-03-06T09:58:22.147Z
"userIdentity": {
2025-03-06T09:58:22.147Z
"type": "AssumedRole",
2025-03-06T09:58:22.147Z
"principalId": "AROAIBY7OLUDPY6JZWQTM:sam-OpsGuardian-EC2",
2025-03-06T09:58:22.147Z
"arn": "arn:aws:sts::753920291680:assumed-role/bu-pw-lambda-cloudops/sam-OpsGuardian-EC2",
2025-03-06T09:58:22.147Z
"accountId": "753920291680",
2025-03-06T09:58:22.147Z
"accessKeyId": "ASIA27CJGWNQNWM34HE4",
2025-03-06T09:58:22.147Z
"sessionContext": {
2025-03-06T09:58:22.147Z
"sessionIssuer": {
2025-03-06T09:58:22.147Z
"type": "Role",
2025-03-06T09:58:22.147Z
"principalId": "AROAIBY7OLUDPY6JZWQTM",
2025-03-06T09:58:22.147Z
"arn": "arn:aws:iam::753920291680:role/hq/bu-pw-lambda-cloudops",
2025-03-06T09:58:22.147Z
"accountId": "753920291680",
2025-03-06T09:58:22.147Z
"userName": "bu-pw-lambda-cloudops"
2025-03-06T09:58:22.147Z
},
2025-03-06T09:58:22.147Z
"attributes": {
2025-03-06T09:58:22.147Z
"creationDate": "2025-03-06T09:48:52Z",
2025-03-06T09:58:22.147Z
"mfaAuthenticated": "false"
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
},
2025-03-06T09:58:22.147Z
"eventTime": "2025-03-06T09:58:18Z",
2025-03-06T09:58:22.147Z
"eventSource": "ec2.amazonaws.com",
2025-03-06T09:58:22.147Z
"eventName": "TerminateInstances",
2025-03-06T09:58:22.147Z
"awsRegion": "us-east-1",
2025-03-06T09:58:22.147Z
"sourceIPAddress": "54.158.64.105",
2025-03-06T09:58:22.147Z
"userAgent": "Boto3/1.34.145 md/Botocore#1.34.145 ua/2.0 os/linux#5.10.233-244.887.amzn2.x86_64 md/arch#x86_64 lang/python#3.11.10 md/pyimpl#CPython exec-env/AWS_Lambda_python3.11 cfg/retry-mode#legacy Botocore/1.34.145",
2025-03-06T09:58:22.147Z
"requestParameters": {
2025-03-06T09:58:22.147Z
"instancesSet": {
2025-03-06T09:58:22.147Z
"items": [
2025-03-06T09:58:22.147Z
{
2025-03-06T09:58:22.147Z
"instanceId": "i-0a7e364ba3c7ef180"
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
]
2025-03-06T09:58:22.147Z
},
2025-03-06T09:58:22.147Z
"force": false,
2025-03-06T09:58:22.147Z
"skipOsShutdown": false
2025-03-06T09:58:22.147Z
},
2025-03-06T09:58:22.147Z
"responseElements": {
2025-03-06T09:58:22.147Z
"requestId": "b3f07297-7e1d-47a7-87b0-89ec9914c103",
2025-03-06T09:58:22.147Z
"instancesSet": {
2025-03-06T09:58:22.147Z
"items": [
2025-03-06T09:58:22.147Z
{
2025-03-06T09:58:22.147Z
"instanceId": "i-0a7e364ba3c7ef180",
2025-03-06T09:58:22.147Z
"currentState": {
2025-03-06T09:58:22.147Z
"code": 32,
2025-03-06T09:58:22.147Z
"name": "shutting-down"
2025-03-06T09:58:22.147Z
},
2025-03-06T09:58:22.147Z
"previousState": {
2025-03-06T09:58:22.147Z
"code": 16,
2025-03-06T09:58:22.147Z
"name": "running"
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
]
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
},
2025-03-06T09:58:22.147Z
"requestID": "b3f07297-7e1d-47a7-87b0-89ec9914c103",
2025-03-06T09:58:22.147Z
"eventID": "ecb76f50-f7a7-45b5-bb3f-a3396f8ca2e8",
2025-03-06T09:58:22.147Z
"readOnly": false,
2025-03-06T09:58:22.147Z
"eventType": "AwsApiCall",
2025-03-06T09:58:22.147Z
"managementEvent": true,
2025-03-06T09:58:22.147Z
"recipientAccountId": "753920291680",
2025-03-06T09:58:22.147Z
"eventCategory": "Management",
2025-03-06T09:58:22.147Z
"tlsDetails": {
2025-03-06T09:58:22.147Z
"tlsVersion": "TLSv1.3",
2025-03-06T09:58:22.147Z
"cipherSuite": "TLS_AES_128_GCM_SHA256",
2025-03-06T09:58:22.147Z
"clientProvidedHostHeader": "ec2.us-east-1.amazonaws.com"
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
}
2025-03-06T09:58:22.147Z
No EC2 instance ID found in event. Skipping.
2025-03-06T09:58:22.148Z
END RequestId: 671d319a-031d-4866-963e-1e8367e12326
