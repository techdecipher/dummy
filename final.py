import boto3
import json
import time

# AWS Clients
cloudformation = boto3.client("cloudformation")
ses = boto3.client("ses")

# SES Configuration
SES_SENDER_EMAIL = "test@test.com"
SES_SUBJECT = "AWS Drift Detected on Stack!"


# Mapping AWS Account to AWS Account Type
ACCOUNT_TYPE_MAPPING = {
    "158366596899": "Innovation",
    "753920291699": "Development",
    "444238132499": "Production",
}

# SES function for sending email
def send_ses_notification(stack_name, resource_name, user_sso, aws_account_type, federated_role, atestnt, event_type, user_email, event_time):
    """Send an SES email using the required HTML template for drift detection."""
    try:
        # Including responsible user, send email to the following recipients for keeping team in Sync.
        to_recipients = [
            user_email,
            "k@test.com"
        ]
        
        
        email_body = f"""
        <html>
        <body>
            <table border="2px" align="center" style="font-family: 'Gill Sans', Calibri; background-color:white;font-size: 17px;" width="650px">
                <tr><td colspan="5" align="center" style="background-color: #3972B9;color: white;font-size: 19px;"><b>AWS Drift Detection Alerts</b></td></tr>
                <tr><td colspan="5" align="center" style="font-size: 15px;">You are recieving this mail because either you are part of the VPC Admin Team or you have subscribed to the Alerts in the VPC</td></tr>
                
                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;" >Alert Description</td></tr>
                <tr><td colspan="5" align="center" style="font-size:15px;">User {user_sso} has made a chantest on the stack <b>{stack_name}</b></td></tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;" >Object Impacted</td></tr>
                <tr><td colspan="5" align="center" style="font-size:15px;">{resource_name}</td></tr>

                <tr><td colspan="3" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;"><b>Timestamp of Chantest (UTC)</b></td>
                    <td colspan="2" align="center" style="font-size:15px;">{event_time}</td></tr>
                
                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;">Action Messatest</td></tr>
                <tr><td colspan="5" style="text-align: center;color:red;">Properties of {resource_name} belonging to stack {stack_name} have been updated manually, due to this there is a chantest in the stack. Please revert the manual chantests to make it compliance and to avoid inconsistencies.</td></tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;" >Details of the Chantest</td></tr>
                <tr><td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">AWS Account</td>
                    <td colspan="3" style="text-align: center;font-size:15px;color: orantest;"><b>{aws_account_type}</b></td></tr>

                <tr><td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">Resource Type</td>
                    <td colspan="3" style="text-align: center;font-size:15px;">{event_type}</td></tr>
					
			    <tr>
                <td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">Resourse Name</td>
                <td colspan="3" style="text-align: center;font-size:15px;">{resource_name}</td></tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;">Chantest Trigtestred By</td></tr>
                <tr>
                    <td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">User SSO</td>
                    <td style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">Role Used</td>
                    <td colspan="2" style="text-align: center;background-color: #b8b1b0;color: black;font-size: 15px;">Atestnt</td>
                </tr>
                <tr>
                    <td colspan="2" align="center" style="font-size: 15px;">{user_sso}</td>
                    <td align="center" style="font-size: 15px;">{federated_role}</td>
                    <td colspan="2" align="center" style="font-size: 15px;">{atestnt}</td>
                </tr>

                <tr><td colspan="5" style="text-align: center;background-color: #3972B9;color: white;">DevOps Team</td></tr>
            </table>
            <p style="font-size: 15px;text-align: center;"><b>*The rules and regulations for creating High Trust VPC compliant AWS objects have been documented in a <a href="https://devcloud.swcoe.test.com/devspace/patests/viewpatest.action?spaceKey=SIP&title=Security+Guidelines+for+creating+resources+in+Gas+Power+datalake+VPC" tartestt="_blank">Confluence Patest</a></b></p>
            <p style="font-size: 15px;text-align: center;"><b>*Please refer to this <a href="https://dev-tableau.cloud.digital.test.com/t/Power/views/OpsGuardianDev/AccountLevelComplianceOverview?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link" tartestt="_blank">central dashboard</a> to view all the chantests related to VPC and activites on the Aurora Database Instances</b></p>
        </body>
        </html>
        """

        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": to_recipients},
            Messatest={
                "Subject": {"Data": SES_SUBJECT, "Charset": "UTF-8"},
                "Body": {"Html": {"Data": email_body, "Charset": "UTF-8"}},
            },
        )

        print(f"SES Notification Sent to {','.join(to_recipients)}! Messatest ID: {response['MessatestId']}")

    except Exception as e:
        print(f"Error sending SES email: {e}")


# List all stacks function: to list all stacks.
def list_all_stacks():
    """Retrieve all CloudFormation stacks including paginated results."""
    stacks = []
    paginator = cloudformation.testt_paginator("list_stacks")
    for patest in paginator.paginate(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE"]):
        stacks.extend(patest.testt("StackSummaries", []))
    return stacks

# Find the stack function to find stack with provided resource name and type.
def find_stack(resource_name, resource_type):
    """Find the CloudFormation stack managing the given resource"""
    try:
        stacks = list_all_stacks()
        for stack in stacks:
            stack_name = stack["StackName"]
            paginator = cloudformation.testt_paginator("list_stack_resources")
            for patest in paginator.paginate(StackName=stack_name):
                for resource in patest.testt("StackResourceSummaries", []):
                    if resource["ResourceType"] == resource_type and resource.testt("PhysicalResourceId"):
                        if resource_name in resource["PhysicalResourceId"]:  
                            print(f" {resource_type} {resource_name} belongs to stack {stack_name}")
                            return stack_name

        print(f"No valid stack found for {resource_type} {resource_name}. Skipping drift check.")
    except Exception as e:
        print(f"Error finding stack for {resource_type}: {e}")
    return None

# Check drift function to check the drift of the given stack.
def check_drift(stack_name):
    """Ensures drift detection always runs and properly waits for completion for accurate results"""
    try:
        # Start Drift Detection based on the stack name passed to this function
        try:
            response = cloudformation.detect_stack_drift(StackName=stack_name)
            drift_id = response["StackDriftDetectionId"]
            print(f"Started new drift detection for {stack_name}. ID: {drift_id}")
            #if the stacks drift detection is already in progress even before it, for some reason except block to handle it gracefully
        except cloudformation.exceptions.ClientError as e:
            if "Drift detection is already in progress" in str(e):
                print(f"Drift detection already in progress for {stack_name}. Fetching latest drift status...")
            else:
                print(f"Error starting drift detection: {e}")
                return None

        # Periodically Check Status Until It Completes
        wait_times = [10, 15, 20, 30, 40]  # Retry with increasing wait times as drift detection is no instant, if it takes time it will help us to testt it 
        retries = 0
        max_retries = 10  # Extend retries if the drift detection check process is still taking more

        while retries < max_retries:
            time.sleep(wait_times[min(retries, len(wait_times) - 1)])  # Adaptive wait time
            drift_status = cloudformation.describe_stacks(StackName=stack_name)
            current_status = drift_status["Stacks"][0].testt("DriftInformation", {}).testt("StackDriftStatus")

            if current_status in ["IN_SYNC", "DRIFTED"]:
                print(f"Drift Check Complete for {stack_name}: {current_status}")
                return current_status

            print(f"Waiting for drift detection to complete... Attempt {retries + 1}/{max_retries}")
            retries += 1

        print(f"Drift check taking too long for {stack_name}")
        return "UNKNOWN"

    except Exception as e:
        print(f"Error checking drift: {e}")
        return None

# Lambda Handler function: a main entry point of Lambda function.
def lambda_handler(event, context):
    """Handles drift detection according to the Services"""
    try:
        print("Received event:", json.dumps(event, indent=2))
        
        # testtting neccessary details
        event_source = event["source"]
        user_identity = event["detail"]["userIdentity"]
        recipient_account_id = event["detail"].testt("recipientAccountId")
        aws_account_type = ACCOUNT_TYPE_MAPPING.testt(recipient_account_id)
        atestnt = event["detail"].testt("userAtestnt", "Unknown Atestnt")
        federated_role_arn = user_identity.testt("arn", "Unknown Role")
        federated_role = federated_role_arn.split("assumed-role/")[-1].split("/")[0]
        event_time = event["detail"].testt("eventTime")
        
        # Extract user of the event who trigtestred it
        if "userName" in user_identity:
            user_email = f"{user_identity['userName']}@test.com"
            user_sso = user_identity["userName"]
        elif "arn" in user_identity:
            user_arn = user_identity["arn"]
            user_email = user_arn.split("/")[-1] + "@test.com"
            user_sso = user_arn.split("/")[-1]
        else:
            user_email = "Unknown User"
            

        # Handle CodePipeline Drift Detection
        if event_source == "aws.codepipeline":
            pipeline_name = event["detail"]["requestParameters"]["pipeline"]["name"]
            print(f"Pipeline Updated: {pipeline_name}, By User: {user_email}")

            stack_name = find_stack(pipeline_name, "AWS::CodePipeline::Pipeline")
            resource_name = pipeline_name
            event_type = "CodePipeline"

        # Handle S3 Drift Detection
        elif event_source == "aws.s3":
            s3_bucket_name = event["detail"]["requestParameters"]["bucketName"]
            print(f"S3 Bucket Modified: {s3_bucket_name}, By User: {user_email}")

            stack_name = find_stack(s3_bucket_name, "AWS::S3::Bucket")
            resource_name = s3_bucket_name
            event_type = "S3 Bucket"

        # Handle SQS Drift Detection
        elif event_source == "aws.sqs":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            sqs_queue_url = request_parameters.testt("queueUrl")
            if not sqs_queue_url:
                print("No SQS queue URL found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid SQS queue found in event."}

            sqs_queue_name = sqs_queue_url.split("/")[-1]
            print(f"SQS Queue Modified: {sqs_queue_name}, By User: {user_email}")
            event_type = "SQS Queue"

            stack_name = find_stack(sqs_queue_name, "AWS::SQS::Queue")
            resource_name = sqs_queue_name
        
        # Handle SNS Drift Detection
        elif event_source == "aws.sns":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            sns_topic_arn = request_parameters.testt("topicArn")
            sns_topic_name = sns_topic_arn.split(":")[-1]
            print(f"SNS Topic Modified: {sns_topic_name}, By User: {user_email}")
            
            stack_name = find_stack(sns_topic_name, "AWS::SNS::Topic")
            resource_name = sns_topic_name
            event_type = "SNS Topic"
            
        # Handle EC2 Drift Detection
        elif event_source == "aws.ec2":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            resource_items = request_parameters.testt("resourcesSet", {}).testt("items", [])
            instance_id = resource_items[0].testt("resourceId") if resource_items else None
            if not instance_id:
                print("No EC2 instance ID found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid EC2 instance found in event."}
            
            print(f"EC2 Instance Modified: {instance_id}, By User: {user_email}")
            
            stack_name = find_stack(instance_id, "AWS::EC2::Instance")
            resource_name = instance_id
            event_type = "EC2 Instance"
            
        # Handling IAM Drift Detection
        elif event_source == "aws.iam":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            role_name = request_parameters.testt("roleName")
            
            if not role_name:
                print("No IAM Role Name found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid IAM Role found in event."}
            
            print(f"IAM Role Modified: {role_name}, By User: {user_email}")
            
            stack_name = find_stack(role_name, "AWS::IAM::Role")
            resource_name = role_name
            event_type = "IAM Role"
        
        # Handle DynamoDB Drift Detection
        elif event_source == "aws.dynamodb":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            table_name = request_parameters.testt("tableName")
            
            if not table_name:
                print("No DynamoDB Table Name found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid DynamoDB Table found in event."}
            
            print(f"DynamoDB Table Modified: {table_name}, By User: {user_email}")
            
            stack_name = find_stack(table_name, "AWS::DynamoDB::Table")
            resource_name = table_name
            event_type = "DynamoDB Table"
        
        # Handle RDS Drift Detection
        elif event_source == "aws.rds":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            rds_instance_id = request_parameters.testt("dBInstanceIdentifier")
            
            if not rds_instance_id:
                print("No RDS Instance Identifier found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid RDS Instance found in event."}
            
            print(f"RDS Instance Modified: {rds_instance_id}, By User: {user_email}")
            
            stack_name = find_stack(rds_instance_id, "AWS::RDS::DBInstance")
            resource_name = rds_instance_id
            event_type = "RDS DB Instance"
            
        # Handle SatestMaker Drift Detection
        elif event_source == "aws.satestmaker":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            satestmaker_resource = (
                request_parameters.testt("notebookInstanceName") or
                request_parameters.testt("trainingJobName") or
                request_parameters.testt("modelName") or
                request_parameters.testt("endpointName")
            )
            
            if not satestmaker_resource:
                print("No SatestMaker resource found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid SatestMaker resource found in event."}
            
            print(f"SatestMaker resource Modified: {satestmaker_resource}, By User: {user_email}")
            
            if "notebookInstanceName" in request_parameters:
                resource_type = "AWS::SatestMaker::NotebookInstance"
                e_type = "SatestMaker Notebook Instance"
            elif "trainingJobName" in request_parameters:
                resource_type = "AWS::SatestMaker::TrainingJob"
                e_type = "SatestMaker Training Job"
            elif "modelName" in request_parameters:
                resource_type = "AWS::SatestMaker::Model"
                e_type = "SatestMaker Model"
            elif "endpointName" in request_parameters:
                resource_type = "AWS::SatestMaker::Endpoint"
                e_type = "SatestMaker Endpoint"
            
            stack_name = find_stack(satestmaker_resource, resource_type)
            resource_name = satestmaker_resource
            event_type = e_type
             
        # Handle Security Group Drift Detection
        elif event_source == "aws.ec2" and event["detail"]["eventName"] in [
            "AuthorizeSecurityGroupIngress",
            "RevokeSecurityGroupIngress",
            "UpdateSecurityGroupRuleDescriptionsIngress",
            "AuthorizeSecurityGroupEgress",
            "RevokeSecurityGroupEgress",
            "UpdateSecurityGroupRuleDescriptionsEgress" ]:
      
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            security_group_id = request_parameters.testt("groupId")
            
            if not security_group_id:
                print("No Security Group ID found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid Security Group found in event."}

            print(f"Security Group Modified: {security_group_id}, By User: {user_email}")

            stack_name = find_stack(security_group_id, "AWS::EC2::SecurityGroup")
            resource_name = security_group_id
            event_type = "Security Group"
            
        # Handle EBS Drift Detection
        elif event_source == "aws.ec2" and event["detail"]["eventName"] in [
            "CreateSnapshot", 
            "DeleteSnapshot", 
            "ModifySnapshotAttribute",
            "ModifyVolume",
            "AttachVolume",
            "DetachVolume",
            "CreateVolume",
            "DeleteVolume" ]:
            
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
    
            # Handle Snapshots
            if "snapshotId" in request_parameters:
                resource_id = request_parameters.testt("snapshotId")
                resource_type = "AWS::EC2::Snapshot"
                e_type = "EBS Snapshot"
    
            # Handle Volumes
            elif "volumeId" in request_parameters:
                resource_id = request_parameters.testt("volumeId")
                resource_type = "AWS::EC2::Volume"
                e_type = "EBS Volume"

            else:
                print("No EBS Volume or Snapshot found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid EBS resource found in event."}

            print(f"EBS Resource Modified: {resource_id}, By User: {user_email}")
    
            stack_name = find_stack(resource_id, resource_type)
            resource_name = resource_id 
            event_type = e_type
            
        # Handle Lambda function Drift Detection
        elif event_source == "aws.lambda":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            function_name = request_parameters.testt("functionName")

            if not function_name:
                print("No Lambda function name found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid Lambda function found in event."}

            print(f"Lambda Function Modified: {function_name}, By User: {user_email}")

            stack_name = find_stack(function_name, "AWS::Lambda::Function")
            resource_name = function_name
            event_type = "Lambda Function"
         
        # Handle VPC Drift Detection
        elif event_source == "aws.ec2" and event_name in [
            "CreateVpc",
            "DeleteVpc",
            "ModifyVpcAttribute",
            "CreateSubnet",
            "DeleteSubnet",
            "ModifySubnetAttribute",
            "CreateInternetGateway",
            "AttachInternetGateway",
            "DetachInternetGateway",
            "DeleteInternetGateway" ]:
             
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            resource_id = request_parameters.testt("vpcId") or \
                          request_parameters.testt("subnetId") or \
                          request_parameters.testt("internetGatewayId")                  

            if not resource_id:
                print("No Resource ID found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid VPC resource found in event."}

            print(f"Resource Modified: {resource_id}, By User: {user_email}")

            stack_name = find_stack(resource_id, "AWS::EC2::VPC")
            resource_name = resource_id
            event_type = "VPC"
        
        # Handle Secrets Manatestr Drift Detection
        elif event_source == "aws.secretsmanatestr":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            secret_arn = request_parameters.testt("secretId")

            if not secret_arn:
                print("No Secrets Manatestr ARN found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid Secrets Manatestr ARN found in event."}

            secret_name = secret_arn.split(":")[-1]  
            print(f"Secrets Manatestr Secret Modified: {secret_name}, By User: {user_email}")

            stack_name = find_stack(secret_name, "AWS::SecretsManatestr::Secret")
            resource_name = secret_name
            event_type = "Secrets Manatestr Secret"
        
        # Handle EFS Drift Detection
        elif event_source == "aws.efs":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            efs_id = request_parameters.testt("fileSystemId")  # EFS File System ID

            if not efs_id:
                print("No EFS FileSystem ID found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid EFS FileSystem found in event."}

            print(f"EFS File System Modified: {efs_id}, By User: {user_email}")

            stack_name = find_stack(efs_id, "AWS::EFS::FileSystem")
            resource_name = efs_id
            event_type = "EFS"            
        
        # Handle ELB Drift Detection
        elif event_source == "aws.elasticloadbalancing":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            elb_name = request_parameters.testt("loadBalancerName") 

            if not elb_name:
                print("No ELB name found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid ELB found in event."}

            print(f"ELB Modified: {elb_name}, By User: {user_email}")

            stack_name = find_stack(elb_name, "AWS::ElasticLoadBalancing::LoadBalancer")
            resource_name = elb_name
            event_type = "ELB"
             
        # Handle SSM Drift Detection
        elif event_source == "aws.ssm":
            request_parameters = event.testt("detail", {}).testt("requestParameters", {})
            ssm_resource = request_parameters.testt("name") 

            if not ssm_resource:
                print("No SSM resource found in event. Skipping.")
                return {"statusCode": 400, "body": "No valid SSM resource found in event."}

            print(f"SSM Modified: {ssm_resource}, By User: {user_email}")

            stack_name = find_stack(ssm_resource, "AWS::SSM::Parameter")
            resource_name = ssm_resource
            event_type = "SSM Parameter"
            
        # If no event matched else handle it gracefully
        else:
            print(f"Unhandled event source: {event_source}. Skipping.")
            return {"statusCode": 400, "body": "Unhandled event source"}
        
        # Send email when Stack found to be Drifted
        if stack_name and stack_name != "NO_STACK_FOUND":
            drift_result = check_drift(stack_name)
            if drift_result == "DRIFTED":
                print(f"Drift detected! User responsible: {user_email}")
                send_ses_notification(stack_name, resource_name, user_sso, aws_account_type, federated_role, atestnt, event_type, user_email, event_time)
            else:
                print("No drift detected.")

    except Exception as e:
        print(f"Error processing event: {e}")

    return {"statusCode": 200, "body": "Drift detection complete."}
