
# ---------------------------------------------------------------------------------------------------------------------
# TERRAGRUNT CONFIGURATION
# This is the configuration for Terragrunt, a thin wrapper for Terraform that supports locking and enforces best
# practices: https://github.com/gruntwork-io/terragrunt
# ---------------------------------------------------------------------------------------------------------------------

# Terragrunt will copy the Terraform configurations specified by the source parameter, along with any files in the
# working directory, into a temporary folder, and execute your Terraform commands in that folder.
terraform {
  source = "git@github.com:tiktok-Motor-North-America/ace-aws-infra-modules.git//storage/s3/bucket?ref=v31.1.8"
}

# Include all settings from the root terragrunt.hcl file
include {
  path = find_in_parent_folders()
}

# Local variables
# Pull required parameters set in the parameter files of this relative path to be used as values.
locals {
  global_vars      = read_terragrunt_config(find_in_parent_folders("global.hcl"))
  region_vars      = read_terragrunt_config(find_in_parent_folders("region.hcl"))
  environment_vars = read_terragrunt_config(find_in_parent_folders("environment.hcl"))
  name_prefix      = local.global_vars.locals.name_prefix
  environment      = local.environment_vars.locals.environment
  aws_region_cd    = local.region_vars.locals.aws_region_cd
}

# ---------------------------------------------------------------------------------------------------------------------
# MODULE PARAMETERS
# These are the variables we have to pass in to use the module specified in the Terragrunt configuration above
# ---------------------------------------------------------------------------------------------------------------------

inputs = {
# Required
# application_id   = ""
# application_name = ""
bucket_name      = "tbdp-pnp-stage-dev"
created_by_email = "jeevan.sagiraju@tiktok.com"
data_classification = "protected"
# environment      = ""

# Booleans
access_logging_enabled = true
allow_encrypted_uploads_only = false
allow_ssl_requests_only = false

enable_datadog_monitoring = true
force_destroy = false
lambda_notifications_create_permission = false
sns_notifications_create_policy = false
sqs_notifications_create_policy = false
versioning_enabled = true
s3_replication_enabled = false
multi_region = false

# Encryption
allow_override_iam_delegation = true
cmk_create_key = true
cmk_key_name = "tbdp-pnp-stage-dev-encrypt-kms-key"
enable_bucket_key = true
customer_master_keys = {
  cmk_administrator_iam_arns = [   
    "arn:aws:iam::000000000000:role/ATD_TBDP-Admin-NonProd",
    "arn:aws:iam::000000000000:role/app-admin-role",
    "arn:aws:iam::000000000000:role/TBDPT_gha_oidc_iam_role",
    "arn:aws:iam::000000000000:role/tbdp-terraform-infra-deploy-role",
  ]  
  cmk_user_iam_arns = [
  {      
    name = [
      "arn:aws:iam::000000000000:role/app-admin-role"
    ]
    conditions = []
  }  
  ]  
  cmk_service_principals = [
  /*{ 
    name       = "s3.amazonaws.com"
    actions    = ["kms:*"]
    conditions = []
  }*/
  ]
  allow_manage_key_permissions_with_iam = false
}

# Optional 
accesslogs_bucketname = "tbdp-comp-logs-dev-comp"
accesslogs_bucketprefix = "s3_access_logs/tbdp-pnp-stage-dev/"
#cmk_existing_key_arn = null 
#cors_configuration = null 
 custom_tags = {
  "Name" = "tbdp-pnp-stage-dev"
  "ApplicationId" = "BS20170035"
  "ApplicationName" = "TBDP-COMP"
  "Description" = "S3 Bucket for all TBDP COMP bucket logs"
  "Domain" = "customer"
  "app_name" = "comp"
  "s3_code_bucket_prefix" = "tbdp-comp-code"
  "s3_logs_bucket_prefix" = "tbdp-comp-logs"
} 
#lambda_notifications = {} 
lifecycle_configuration_rules = [{
  enabled = true
  id      = "TBDP SOX Lifecycle Rules"

  abort_incomplete_multipart_upload_days = 7
  filter_and                             = null

  transition = [{
    days          = 7
    storage_class = "INTELLIGENT_TIERING"
  }]

  expiration = {
    expired_object_delete_marker = true
  }

  noncurrent_version_transition = [{
    newer_noncurrent_versions = 1
    noncurrent_days           = 7
    storage_class             = "INTELLIGENT_TIERING"
  }]

  noncurrent_version_expiration = {
    newer_noncurrent_versions = 1
    noncurrent_days           = 30
  }

}]
 
#logging_source_policy_documents = [] 
logging_lifecycle_configuration_rules = [{
  enabled    = true
  id         = "log_bucket_lifecycle"
  filter_and = null
  # Delete logs after 1 year
  expiration = {
    days = 365
  }
}]
 
#sns_notifications = {}
source_policy_documents = [jsonencode({
  "Version": "2012-10-17",
  "Statement": [
        {
            "Sid": "UpdateBucketPolicy",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::000000000000:root"
            },
            "Action": "s3:PutBucketPolicy",
            "Resource": "arn:aws:s3:::tbdp-pnp-stage-dev"
        },
        {
            "Sid": "ListBucket",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::000000000000:root"
            },
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::tbdp-pnp-stage-dev"
        },
        {
            "Sid": "AllowAccessForADGroups",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                  "arn:aws:iam::000000000000:role/tbdd-dvpr",
                  "arn:aws:iam::000000000000:role/tbdd-sox-sap-test"
                ]
            },
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::tbdp-pnp-stage-dev",
                "arn:aws:s3:::tbdp-pnp-stage-dev/*"
            ]
        },
        {
            "Sid": "DenyBucketAccessExceptWhiteListed",
            "Effect": "Deny",
            "Principal": "*",
            "NotAction": [
                "s3:Get*",
                "s3:List*"
            ],
            "Resource": "arn:aws:s3:::tbdp-pnp-stage-dev",
            "Condition": {
                "StringNotLike": {
                    "aws:PrincipalArn": [
                        "arn:aws:iam::000000000000:role/tbdp-terraform-infra-deploy-role",
                        "arn:aws:iam::000000000000:role/app-admin-role",
                        "arn:aws:iam::000000000000:role/TBDPT_gha_oidc_iam_role",
                        "arn:aws:iam::000000000000:role/tbdp-s3-common-replication-role",
                        "arn:aws:iam::000000000000:role/atd_tbdp-ops_admin_dev-role",
                        "arn:aws:iam::000000000000:user/dna_tbdp-comp-sox-dev_nonprod_svc",
                        "arn:aws:iam::000000000000:role/tbdd-comp-databricks-s3-dev",
                        "arn:aws:iam::000000000000:role/tbdd-comp-svc-role",
                        "arn:aws:iam::000000000000:role/tbdd-dvpr",
                        "arn:aws:iam::000000000000:role/tbdd-sox-sap-test"
                    ]
                }
            }
        },
        {
            "Sid": "DenyObjectAccessExceptWhiteListed",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::tbdp-pnp-stage-dev/*",
            "Condition": {
                "StringNotLike": {
                    "aws:PrincipalArn": [
                        "arn:aws:iam::000000000000:role/tbdp-terraform-infra-deploy-role",
                        "arn:aws:iam::000000000000:role/app-admin-role",
                        "arn:aws:iam::000000000000:role/TBDPT_gha_oidc_iam_role",
                        "arn:aws:iam::000000000000:role/tbdp-s3-common-replication-role",
                        "arn:aws:iam::000000000000:role/atd_tbdp-ops_admin_dev-role",
                        "arn:aws:iam::000000000000:user/dna_tbdp-comp-sox-dev_nonprod_svc",
                        "arn:aws:iam::000000000000:role/tbdd-comp-databricks-s3-dev",
                        "arn:aws:iam::000000000000:role/tbdd-comp-svc-role",
                        "arn:aws:iam::000000000000:role/tbdd-dvpr",
                        "arn:aws:iam::000000000000:role/tbdd-sox-sap-test"
                    ]
                }
            }
         }
  ]
})]
#sqs_notifications = {} 
team = "tbdpt"  
#s3_replication_rules = [] 
#s3_replica_bucket_arn = ""  
#cmk_replica_existing_key_arn = null 
}
