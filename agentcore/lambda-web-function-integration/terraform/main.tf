data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "random_string" "prefix" {
  length  = 4
  special = false
  upper   = false
  numeric = false
}

locals {
  region       = data.aws_region.current.region
  account_id   = data.aws_caller_identity.current.account_id
  prefix       = random_string.prefix.id
  project_name = "${local.prefix}-agentcore-lambda-web-function-integration"
}






