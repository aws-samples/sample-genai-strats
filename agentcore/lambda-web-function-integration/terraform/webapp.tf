locals {
  webapp_src_dir       = abspath("${path.module}/../webapp")
  webapp_function_name = "${local.prefix}-webapp"
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
  # Changes on every plan, so npm ci runs on every terraform apply.
  triggers_replace = plantimestamp()

  provisioner "local-exec" {
    working_dir = local.webapp_src_dir
    command     = "npm ci --omit=dev"
  }
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
# Covers the whole bucket because `aws lambda-web deploy` picks its own object keys.
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
        Resource = "${aws_s3_bucket.webapp.arn}/*"
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

# Owns the Web Function's lifecycle: deletes it on terraform destroy. Kept separate from the deploy
# step below, which is replaced on every code change and must not delete the function each time.
resource "terraform_data" "web_function" {
  input = {
    name = local.webapp_function_name
  }

  provisioner "local-exec" {
    when    = destroy
    command = "aws lambda-web delete-web-function --function-name ${self.input.name}"
  }
}

# The AWS::Lambda::WebFunction CloudFormation type (used by awscc and Cloud Control) currently
# rejects nodejs24.x, so the function is deployed with the Lambda Web API instead. `deploy` packages the webapp, uploads it, and
# creates the function or adds a new revision; the endpoint serves the latest revision.
resource "terraform_data" "web_function_deploy" {
  triggers_replace = [
    sha256(join("", [
      for f in sort(fileset(local.webapp_src_dir, "**")) :
      filesha256("${local.webapp_src_dir}/${f}") if !startswith(f, "node_modules/")
    ])),
    terraform_data.web_function.output.name,
    time_sleep.webapp_role_propagation.triggers["role_arn"],
    aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn,
  ]

  provisioner "local-exec" {
    environment = {
      AWS_PAGER = ""
    }
    command = <<-EOT
      set -euo pipefail
      aws lambda-web deploy --create \
        --name ${terraform_data.web_function.output.name} \
        --code ${local.webapp_src_dir} \
        --bucket-name ${aws_s3_bucket.webapp.bucket} \
        --execution-role-arn ${time_sleep.webapp_role_propagation.triggers["role_arn"]} \
        --env AGENT_RUNTIME_ARN=${aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn} \
        --endpoint-name ${local.webapp_endpoint_name} \
        --endpoint-type HomeRegion \
        --auth-type ApplicationManaged

      aws lambda-web get-web-function-endpoint \
        --function-name ${terraform_data.web_function.output.name} \
        --endpoint-name ${local.webapp_endpoint_name} \
        --query domainName --output text > ${path.root}/../tmp/webapp_domain_name.txt
    EOT
  }

  depends_on = [
    terraform_data.install_dependencies,
    aws_s3_bucket_versioning.webapp,
    aws_s3_bucket_policy.webapp,
  ]
}

# The deploy step writes the endpoint's domain to this file; depends_on defers reading it
# until after a deploy whenever one is pending.
data "local_file" "webapp_domain_name" {
  filename = "${path.root}/../tmp/webapp_domain_name.txt"

  depends_on = [terraform_data.web_function_deploy]
}

output "webapp_url" {
  value = "https://${trimspace(data.local_file.webapp_domain_name.content)}/"
}
