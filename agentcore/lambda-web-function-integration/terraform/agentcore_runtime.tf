resource "aws_iam_role" "agent" {
  name = local.project_name

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

locals {
  # Passed to the agent as the MODEL_ID env var.
  agent_model_id              = "us.anthropic.claude-haiku-5-5"
  agent_inference_profile_arn = "arn:aws:bedrock:${local.region}:${local.account_id}:inference-profile/${local.agent_model_id}"
}

resource "aws_iam_role_policy" "agent" {
  role = aws_iam_role.agent.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ]
        Resource = local.agent_inference_profile_arn
      },
      {
        # The cross-region inference profile routes to the foundation model in multiple regions;
        # allow those only when invoked through the profile above.
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ]
        Resource = "arn:aws:bedrock:*::foundation-model/${trimprefix(local.agent_model_id, "us.")}"
        Condition = {
          StringEquals = {
            "bedrock:InferenceProfileArn" = local.agent_inference_profile_arn
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
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

  environment_variables = {
    MODEL_ID = local.agent_model_id
  }

  agent_runtime_artifact {
    container_configuration {
      container_uri = local.full_ecr_image_uri_with_digest
    }
  }

  network_configuration {
    network_mode = "PUBLIC"
  }
}

resource "local_file" "agent_runtime_arn" {
  content  = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
  filename = "${path.root}/../tmp/agent_runtime_arn.txt"
}

