locals {
  webapp_src_dir       = abspath("${path.module}/../webapp")
  webapp_zip           = abspath("${path.module}/../tmp/webapp.zip")
  webapp_s3_key        = "webapp.zip"
  webapp_function_name = local.project_name
  webapp_endpoint_name = "default"
}

resource "aws_s3_bucket" "webapp" {
  bucket        = "${local.project_name}-${local.account_id}"
  force_destroy = true
}

# Lambda Web Functions deploy code from a specific object version, so the bucket must be versioned.
resource "aws_s3_bucket_versioning" "webapp" {
  bucket = aws_s3_bucket.webapp.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Install production dependencies into webapp/node_modules.
resource "terraform_data" "install_dependencies" {
  # Reinstall when dependencies change, or when node_modules is missing (e.g. a fresh clone).
  triggers_replace = [
    filesha256("${local.webapp_src_dir}/package.json"),
    filesha256("${local.webapp_src_dir}/package-lock.json"),
    fileexists("${local.webapp_src_dir}/node_modules/.package-lock.json"),
  ]

  provisioner "local-exec" {
    working_dir = local.webapp_src_dir
    command     = "npm ci --omit=dev"
  }
}

# depends_on defers reading this until after npm ci when deps are being reinstalled,
# so the zip always includes node_modules.
data "archive_file" "webapp" {
  type        = "zip"
  source_dir  = local.webapp_src_dir
  output_path = local.webapp_zip

  depends_on = [terraform_data.install_dependencies]
}

resource "aws_s3_object" "webapp" {
  bucket      = aws_s3_bucket.webapp.bucket
  key         = local.webapp_s3_key
  source      = data.archive_file.webapp.output_path
  source_hash = data.archive_file.webapp.output_base64sha256

  depends_on = [aws_s3_bucket_versioning.webapp]
}

resource "aws_iam_role" "webapp" {
  name = "${local.project_name}-webapp"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "webapp" {
  role = aws_iam_role.webapp.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Lambda writes logs to the ".local" log group in every Region where an endpoint
        # serves traffic, then centralizes them into the log group in the home Region.
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/web/${local.webapp_function_name}:*",
          "arn:aws:logs:*:${local.account_id}:log-group:/aws/lambda/web/${local.webapp_function_name}.local:*",
        ]
      },
      {
        # The webapp backend calls this one agent runtime.
        Effect = "Allow"
        Action = "bedrock-agentcore:InvokeAgentRuntime"
        Resource = [
          aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn,
          "${aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn}/*",
        ]
      }
    ]
  })
}

# At deploy time Lambda fetches the code zip as the service principal (not the execution role),
# authorized by this bucket policy. Scoped to this account to avoid the confused-deputy problem.
resource "aws_s3_bucket_policy" "webapp" {
  bucket = aws_s3_bucket.webapp.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
        ]
        Resource = "${aws_s3_bucket.webapp.arn}/${local.webapp_s3_key}"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = local.account_id
          }
        }
      }
    ]
  })
}

# A newly created IAM role takes a few seconds to propagate before Lambda can assume it.
resource "time_sleep" "webapp_role_propagation" {
  create_duration = "15s"

  triggers = {
    role_arn = aws_iam_role.webapp.arn
  }

  depends_on = [aws_iam_role_policy.webapp]
}

resource "awscc_lambda_web_function" "webapp" {
  function_name = local.webapp_function_name
}

# Revisions are immutable, so every new code version (or config change) replaces this resource.
# create_before_destroy lets the endpoint switch to the new revision before the old one is deleted.
resource "awscc_lambda_web_function_revision" "webapp" {
  function_name = awscc_lambda_web_function.webapp.function_name

  build_config = {
    code_config = {
      s3_object = {
        bucket     = aws_s3_bucket.webapp.bucket
        key        = aws_s3_object.webapp.key
        version_id = aws_s3_object.webapp.version_id
      }
    }
    runtime_config = {
      runtime = "nodejs24.x"
    }
  }

  service_config = {
    execution_role_arn = time_sleep.webapp_role_propagation.triggers["role_arn"]
    environment_variables = {
      AGENT_RUNTIME_ARN = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
    }
  }

  depends_on = [aws_s3_bucket_policy.webapp]

  lifecycle {
    create_before_destroy = true
  }
}

resource "awscc_lambda_web_function_endpoint" "webapp" {
  function_name = awscc_lambda_web_function.webapp.function_name
  endpoint_name = local.webapp_endpoint_name
  endpoint_type = "HomeRegion"
  auth_type     = "ApplicationManaged"

  revision_weights = [{
    revision_id = awscc_lambda_web_function_revision.webapp.revision_id
    weight      = 100
  }]
}

output "webapp_url" {
  value = "https://${awscc_lambda_web_function_endpoint.webapp.domain_name}/"
}
