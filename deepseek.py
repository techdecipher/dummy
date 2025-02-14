import boto3

# Initialize AWS clients
cloudformation = boto3.client('cloudformation')

def list_all_stacks():
    """Retrieve all CloudFormation stacks including paginated results."""
    stacks = []
    paginator = cloudformation.get_paginator("list_stacks")
    for page in paginator.paginate(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE"]):
        stacks.extend(page.get("StackSummaries", []))
    return stacks

def find_stack(resource_name, resource_type):
    """Find the CloudFormation stack managing the given resource, with pagination."""
    try:
        stacks = list_all_stacks()
        for stack in stacks:
            stack_name = stack["StackName"]
            paginator = cloudformation.get_paginator("list_stack_resources")
            for page in paginator.paginate(StackName=stack_name):
                for resource in page.get("StackResourceSummaries", []):
                    if resource["ResourceType"] == resource_type and resource.get("PhysicalResourceId"):
                        if resource_name in resource["PhysicalResourceId"]:  # Allow partial match
                            print(f"✅ {resource_type} {resource_name} belongs to stack {stack_name}")
                            return stack_name

        print(f"🚫 No valid stack found for {resource_type} {resource_name}. Skipping drift check.")
    except Exception as e:
        print(f"❌ Error finding stack for {resource_type}: {e}")
    return None
