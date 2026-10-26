locals {
  project_name_underscore = replace(var.project_name, "-", "_")

  # Must match the model_id in src/agent/agent.py
  agent_model_id = "us.anthropic.claude-sonnet-4-6"

  # ARNs of the resources the agent uses, built from their IDs and names
  memory_arn              = "arn:aws:bedrock-agentcore:${var.region}:${var.account_id}:memory/${var.agentcore_memory_id}"
  knowledge_base_arn      = "arn:aws:bedrock:${var.region}:${var.account_id}:knowledge-base/${var.tech_support_knowledgebase_id}"
  workload_directory_arn  = "arn:aws:bedrock-agentcore:${var.region}:${var.account_id}:workload-identity-directory/default"
  workload_identity_arn   = "${local.workload_directory_arn}/workload-identity/${var.workload_identity_name}"
  token_vault_arn         = "arn:aws:bedrock-agentcore:${var.region}:${var.account_id}:token-vault/default"
  credential_provider_arn = "${local.token_vault_arn}/oauth2credentialprovider/${var.credential_provider_name}"
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

resource "aws_iam_role_policy" "agent" {
  role = aws_iam_role.agent.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # To subscribe to Bedrock Models
        Effect = "Allow"
        Action = [
          "aws-marketplace:Subscribe",
          "aws-marketplace:ViewSubscriptions",
          "aws-marketplace:Unsubscribe",
        ]
        Resource = "*"
      },
      {
        # To invoke the agent's model. The cross-region inference profile routes requests
        # to the foundation model in other US regions, so both are needed.
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ]
        Resource = [
          "arn:aws:bedrock:${var.region}:${var.account_id}:inference-profile/${local.agent_model_id}",
          "arn:aws:bedrock:*::foundation-model/${trimprefix(local.agent_model_id, "us.")}",
        ]
      },
      {
        # To retrieve technical support documents from the Knowledge Base
        Effect   = "Allow"
        Action   = ["bedrock:Retrieve"]
        Resource = local.knowledge_base_arn
      },
      {
        # To read and write conversations in AgentCore Memory
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:CreateEvent",
          "bedrock-agentcore:GetEvent",
          "bedrock-agentcore:ListEvents",
          "bedrock-agentcore:RetrieveMemoryRecords",
        ]
        Resource = local.memory_arn
      },
      {
        # To get the agent's workload access token from AgentCore Identity
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:GetWorkloadAccessToken",
          "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
          "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
        ]
        Resource = [
          local.workload_directory_arn,
          local.workload_identity_arn,
        ]
      },
      {
        # To exchange the workload access token for a gateway access token from the credential provider
        Effect = "Allow"
        Action = ["bedrock-agentcore:GetResourceOauth2Token"]
        Resource = [
          local.workload_directory_arn,
          local.workload_identity_arn,
          local.token_vault_arn,
          local.credential_provider_arn,
        ]
      },
      {
        # To write the agent's logs
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:DescribeLogStreams",
        ]
        Resource = "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
      },
      {
        Effect   = "Allow"
        Action   = ["logs:DescribeLogGroups"]
        Resource = "arn:aws:logs:${var.region}:${var.account_id}:log-group:*"
      },
      {
        # To send traces and metrics. X-Ray doesn't support resource-level permissions.
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets",
        ]
        Resource = "*"
      },
      {
        Effect    = "Allow"
        Action    = "cloudwatch:PutMetricData"
        Resource  = "*"
        Condition = { StringEquals = { "cloudwatch:namespace" = "bedrock-agentcore" } }
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = "arn:aws:secretsmanager:${var.region}:${var.account_id}:secret:*${var.credential_provider_name}*"
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

output "agent_runtime_id" {
  value = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_id
}

resource "local_file" "agent_runtime_arn" {
  content  = local.agent_runtime_arn
  filename = "${path.root}/../tmp/agent_runtime_arn.txt"
}
