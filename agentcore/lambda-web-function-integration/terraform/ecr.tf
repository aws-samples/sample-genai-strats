locals {
  agent_src_dir   = "${path.module}/../agent"
  agent_image_tag = "latest"
  ecr_registry    = "${local.account_id}.dkr.ecr.${local.region}.amazonaws.com"
  agent_image_uri = "${aws_ecr_repository.agent.repository_url}:${local.agent_image_tag}"
}

resource "aws_ecr_repository" "agent" {
  name         = local.project_name
  force_delete = true
}

resource "terraform_data" "agent_image" {
  triggers_replace = [
    filesha256("${local.agent_src_dir}/Dockerfile"),
    filesha256("${local.agent_src_dir}/main.py"),
    filesha256("${local.agent_src_dir}/pyproject.toml"),
    filesha256("${local.agent_src_dir}/uv.lock"),
    local.agent_image_uri,
  ]

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command     = <<-EOT
      set -euo pipefail
      aws ecr get-login-password --region ${local.region} \
        | docker login --username AWS --password-stdin ${local.ecr_registry}
      docker build --platform linux/arm64 -t ${local.agent_image_uri} ${local.agent_src_dir}
      docker push ${local.agent_image_uri}
    EOT
  }

  depends_on = [aws_ecr_repository.agent]
}

# Resolve the digest of the pushed image so consumers pick up every new build.
data "aws_ecr_image" "agent" {
  repository_name = aws_ecr_repository.agent.name
  image_tag       = local.agent_image_tag

  depends_on = [terraform_data.agent_image]
}

locals {
  full_ecr_image_uri_with_digest = "${aws_ecr_repository.agent.repository_url}@${data.aws_ecr_image.agent.image_digest}"
}
