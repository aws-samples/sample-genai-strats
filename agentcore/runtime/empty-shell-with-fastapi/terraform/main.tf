data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "random_string" "prefix" {
  length  = 4
  special = false
  upper   = false
  numeric = false
}

locals {
  prefix = random_string.prefix.id
  project_name = "${local.prefix}-empty-shell-with-fastapi"
  region = data.aws_region.current.region
  account_id = data.aws_caller_identity.current.account_id
}

module "bootstrap" {
  source = "./bootstrap"
  ecr_repo_name = local.project_name
  region = local.region
  account_id = local.account_id
}





