terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.60"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = "~> 1.97"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }

  }
}

provider "aws" {}

provider "awscc" {}

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
  short_project_name = "ac-with-wd-idp"
  project_name = "${random_string.prefix.id}-${local.short_project_name}"
  project_name_underscore = replace(local.project_name, "-","_")
}
