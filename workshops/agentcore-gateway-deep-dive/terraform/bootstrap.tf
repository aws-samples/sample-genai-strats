data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "random_string" "prefix" {
  length  = 4
  special = false
  upper   = false
  numeric = false
}

locals {
  prefix                  = random_string.prefix.id
  project_name_short      = "pizza-gateway"
  project_name            = "${local.prefix}-${local.project_name_short}"
  project_name_underscore = replace(local.project_name, "-", "_")
  account_id              = data.aws_caller_identity.current.account_id
  region                  = data.aws_region.current.region
}
