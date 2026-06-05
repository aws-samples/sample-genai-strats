locals {
  project_name_underscore = replace(var.project_name, "-", "_")
}

resource "aws_iam_role" "agent" {
  name = "${var.project_name}-agent"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock-agentcore.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

data "aws_caller_identity" "current" {}

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

          # To use Bedrock Knowledge Base and AgentCore Memory
          "bedrock:*",
          "bedrock-agentcore:*",

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
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = "arn:aws:secretsmanager:${var.region}:${data.aws_caller_identity.current.account_id}:secret:*${var.credential_provider_name}*"
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

  environment_variables = {
    AGENT_ZIP_ETAG           = filemd5("${path.root}/../tmp/agent_package/agent.zip")
    MEMORY_ID                = var.agentcore_memory_id
    TECH_SUPPORT_KB_ID       = var.tech_support_knowledgebase_id
    GATEWAY_URL              = var.gateway_url
    COGNITO_SCOPE            = var.cognito_scope
    WORKLOAD_ID_NAME         = var.workload_identity_name
    CREDENTIAL_PROVIDER_NAME = var.credential_provider_name
  }

  network_configuration {
    network_mode = "PUBLIC"
  }
}

locals {
  agent_runtime_arn         = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
  agent_runtime_arn_encoded = replace(local.agent_runtime_arn, "/", "%2F")
  agent_runtime_url         = "https://bedrock-agentcore.${var.region}.amazonaws.com/runtimes/${local.agent_runtime_arn_encoded}/invocations/"
}

output "runtime_arn" {
  value = aws_bedrockagentcore_agent_runtime.agent
}

resource "local_file" "agent_runtime_arn" {
  content  = local.agent_runtime_arn
  filename = "${path.root}/../tmp/agent_runtime_arn.txt"
}

# output "runtime_url" {
#   value = local.agent_runtime_url
# }

# resource "local_file" "agent_runtime_url" {
#   content  = local.agent_runtime_url
#   filename = "${path.root}/../tmp/agent_runtime_url.txt"
# }


