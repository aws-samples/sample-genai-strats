resource "aws_iam_role" "mcp_server" {
  name = "${local.project_name}-role"

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

resource "aws_iam_role_policy" "mcp_server" {
  role = aws_iam_role.mcp_server.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "logs:PutResourcePolicy"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.mcp_server.arn}/${aws_s3_object.mcp_server_package_zip.key}"
      }
    ]
  })
}

resource "aws_bedrockagentcore_agent_runtime" "mcp_server" {
  agent_runtime_name = replace(local.project_name, "-", "_")
  role_arn           = aws_iam_role.mcp_server.arn

  agent_runtime_artifact {
    code_configuration {
      entry_point = ["server.py"]
      runtime     = "PYTHON_3_13"
      code {
        s3 {
          bucket = aws_s3_object.mcp_server_package_zip.bucket
          prefix = aws_s3_object.mcp_server_package_zip.key
        }
      }
    }
  }

  authorizer_configuration {
    custom_jwt_authorizer {
      discovery_url   = local.cognito_discovery_url
      allowed_clients = [aws_cognito_user_pool_client.this.id]
    }
  }

  protocol_configuration {
    server_protocol = "MCP"
  }

  network_configuration {
    network_mode = "PUBLIC"
  }
}

locals {
  mcp_server_runtime_arn         = aws_bedrockagentcore_agent_runtime.mcp_server.agent_runtime_arn
  mcp_server_runtime_arn_encoded = replace(local.mcp_server_runtime_arn, "/", "%2F")
  mcp_server_runtime_url         = "https://bedrock-agentcore.${local.region}.amazonaws.com/runtimes/${local.mcp_server_runtime_arn_encoded}/invocations/"
}


output "runtime_arn" {
  value = aws_bedrockagentcore_agent_runtime.mcp_server.agent_runtime_arn
}

resource "local_file" "runtime_arn" {
  content  = aws_bedrockagentcore_agent_runtime.mcp_server.agent_runtime_arn
  filename = "${path.root}/../tmp/runtime_arn.txt"
}

output "runtime_url" {
  value = local.mcp_server_runtime_url
}

resource "local_file" "untime_url" {
  content  = local.mcp_server_runtime_url
  filename = "${path.root}/../tmp/runtime_url.txt"
}
