resource "aws_iam_role" "agent" {
  name = "${local.project_name}-agent"

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
        Effect = "Allow"
        Action = [
          # To subscribe to Bedrock Models
          "aws-marketplace:Subscribe",
          "aws-marketplace:ViewSubscriptions",
          "aws-marketplace:Unsubscribe",

          # To invoke Bedrock Models
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",

          # To send telemetry to CloudWatch
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_bedrockagentcore_agent_runtime" "agent" {
  agent_runtime_name = "${local.project_name_underscore}_agent"
  role_arn           = aws_iam_role.agent.arn

  agent_runtime_artifact {
    code_configuration {
      entry_point = ["agent.py"]
      runtime     = "PYTHON_3_13"
      code {
        s3 {
          bucket = aws_s3_object.agent_zip.bucket
          prefix = aws_s3_object.agent_zip.key
        }
      }
    }
  }

  network_configuration {
    network_mode = "PUBLIC"
  }

  environment_variables = {
    WORKLOAD_IDENTITY_NAME   = aws_bedrockagentcore_workload_identity.hr_agent.name
    CREDENTIAL_PROVIDER_NAME = aws_bedrockagentcore_oauth2_credential_provider.workday_agent.name
    AGENT_ZIP_ETAG           = filemd5("${path.root}/../tmp/agent_package/agent.zip")
    AGENT_MODE               = var.wd_agent_mode
    ACCESS_TOKEN             = var.wd_agent_access_token
    MCP_ENDPOINT             = var.wd_agent_mcp_endpoint
    A2A_AGENT_CARD_BASE_URL  = var.wd_agent_card_base_url
  }
}

locals {
  agent_runtime_arn_encoded = replace(aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn, "/", "%2F")
  agent_runtime_url         = "https://bedrock-agentcore.${local.region}.amazonaws.com/runtimes/${local.agent_runtime_arn_encoded}/invocations/"
}

resource "local_file" "agent_runtime_url" {
  content  = local.agent_runtime_url
  filename = "${path.root}/../tmp/agent_runtime_url.txt"
}

resource "local_file" "agent_runtime_arn" {
  content  = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
  filename = "${path.root}/../tmp/agent_runtime_arn.txt"
}

resource "local_file" "agent_runtime_arn_encoded" {
  content  = local.agent_runtime_arn_encoded
  filename = "${path.root}/../tmp/agent_runtime_arn_encoded.txt"
}
