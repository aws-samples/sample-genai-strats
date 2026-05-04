data "aws_ecr_image" "this" {
  repository_name = module.bootstrap.ecr_repo_name
  image_tag = "latest"
}

locals {

  full_ecr_image_uri_with_digest = "${module.bootstrap.ecr_repo_url}@${data.aws_ecr_image.this.image_digest}"
}

resource "aws_iam_role" "agent" {
  name = "${local.project_name}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "bedrock-agentcore.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "agent" {
  role = aws_iam_role.agent.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_bedrockagentcore_agent_runtime" "agent" {
  agent_runtime_name = replace(local.project_name, "-", "_")
  role_arn           = aws_iam_role.agent.arn

  agent_runtime_artifact {
    container_configuration {
      container_uri = local.full_ecr_image_uri_with_digest
    }
  }

  network_configuration {
    network_mode = "PUBLIC"
  }
}

output "agent_runtime_arn" {
  value = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
}

resource "local_file" "agent_runtime_arn" {
  content         = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
  filename        = "${path.module}/../tmp/agent_runtime_arn.txt"
}

