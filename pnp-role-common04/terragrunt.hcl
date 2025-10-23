# ---------------------------------------------------------------------------------------------------------------------
# TERRAGRUNT CONFIGURATION
# This is the configuration for Terragrunt, a thin wrapper for Terraform that supports locking and enforces best
# practices: https://github.com/gruntwork-io/terragrunt
# ---------------------------------------------------------------------------------------------------------------------

# Terragrunt will copy the Terraform configurations specified by the source parameter, along with any files in the
# working directory, into a temporary folder, and execute your Terraform commands in that folder.
terraform {
  source = "git::git@github.com:tiktok-Motor-North-America/tbdpt-pnpaccess-aws-infra-live.git//custom-modules/security/iam/iam-role?ref=develop"
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
  application_id   = local.global_vars.locals.application_id
  application_name = local.global_vars.locals.application_name
}

# ---------------------------------------------------------------------------------------------------------------------
# MODULE PARAMETERS
# These are the variables we have to pass in to use the module specified in the Terragrunt configuration above
# ---------------------------------------------------------------------------------------------------------------------

inputs = {
# Required variables
application_id = local.application_id
application_name = local.application_name
created_by_email = "min@tiktok.com"
role_name = "tbdpt-persona-role"
description = "TBDPT IAM role to access other services. Created through PNP Automation"
max_session_duration = 3600
principals = ["s3.amazonaws.com"]
custom_policy_name = "tbdpt-persona-rw-policy"
policy_arn = "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"

use_existing_iam_role = false
existing_iam_role_name = ""
create_instance_profile = false
instance_profile_name = ""


# Provide customized Trust Relationship Policy. If not, default will be added
assume_policy = [
  {
    "Effect": "Allow",
    "Principal": {
      "Service": [
        "s3.amazonaws.com"
      ]
    },
    "Action": "sts:AssumeRole"
  }
]

custom_policy = [
    {
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::tbdp-comp-*",
                "arn:aws:s3:::tbdp-comp-*/*",
                "arn:aws:s3:::tbdp-*",
                "arn:aws:s3:::tbdp-*/*"
            ],
            "Sid": "S3BucketsAction"
        },
        {
      Action: [
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:Encrypt",
        "kms:DescribeKey",
        "kms:Decrypt"
      ],
      Effect: "Allow",
      Resource: [
        "arn:aws:kms:us-east-1:000000000000:key/0709a1d0-aee4-4bb4-8b95-de27700cfaf2",
        "arn:aws:kms:us-east-1:000000000000:key/25281792-d6c9-42eb-b348-fe8323f92b44",
        "arn:aws:kms:us-east-1:000000000000:key/3631e14d-4c8d-4995-b9c3-b8fa7ffc87bc",
        "arn:aws:kms:us-east-1:000000000000:key/8df6b76f-e539-4bbe-829f-c467b9d15975",
        "arn:aws:kms:us-east-1:000000000000:key/b168fdd6-617c-48f4-8aca-2525c3b8768b",
        "arn:aws:kms:us-east-1:000000000000:key/d8efd350-d682-4520-9463-21c180009221",
        "arn:aws:kms:us-east-1:000000000000:key/8f80d8f9-283b-4558-a33d-02c23c1fa643",
        "arn:aws:kms:us-east-1:000000000000:key/f506006b-5619-42ef-a039-ea59f881e372",
        "arn:aws:kms:us-east-1:000000000000:key/15fad003-7781-490c-be7a-5a14444492fa",
        "arn:aws:kms:us-east-1:000000000000:key/706d8f7d-c246-48d6-9998-e75f80b9341f",
        "arn:aws:kms:us-east-1:000000000000:key/df712501-bf13-4a76-8b2e-28501e0743dd",
        "arn:aws:kms:us-east-1:000000000000:key/591a7f07-63df-4eb0-9daa-ed86f5f897c0"
      ],
      Sid: "KMSAcess"
  }
] 
}
