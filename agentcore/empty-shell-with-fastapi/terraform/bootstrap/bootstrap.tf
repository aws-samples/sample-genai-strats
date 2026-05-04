variable "ecr_repo_name" {}
variable "region" {}
variable "account_id" {}

resource "aws_ecr_repository" "agent" {
    name = var.ecr_repo_name
    force_delete = true
}

output "ecr_repo_name" {
  value = aws_ecr_repository.agent.name
}

output "ecr_repo_url" {
  value = aws_ecr_repository.agent.repository_url
}

resource "local_file" "region" {
  filename = "${path.root}/../tmp/aws_region.txt"
  content  = var.region
}

resource "local_file" "account_id" {
  filename = "${path.root}/../tmp/aws_account_id.txt"
  content  = var.account_id
}

resource "local_file" "ecr_repo_url" {
  filename = "${path.root}/../tmp/ecr_repo_url.txt"
  content  = aws_ecr_repository.agent.repository_url
}
