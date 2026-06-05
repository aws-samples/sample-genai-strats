data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "random_string" "prefix" {
  length  = 4
  special = false
  upper   = false
  numeric = false
}

locals {
  prefix             = random_string.prefix.id
  project_name_short = "building-ai-agents"
  project_name       = "${local.prefix}-${local.project_name_short}"
}

