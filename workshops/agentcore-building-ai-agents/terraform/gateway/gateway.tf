resource "aws_iam_role" "gateway" {
  name = "${var.project_name}-agentcore-gw"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock-agentcore.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "gateway_invoke_lambda" {
  role = aws_iam_role.gateway.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "lambda:InvokeFunction"
      Resource = [
        aws_lambda_function.tool_check_warranty_status.arn,
      ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]

        Resource = "*"
    }]
  })
}

resource "aws_bedrockagentcore_gateway" "customer_support" {
  name        = "${var.project_name}-customersupport-gw"
  description = "MCP gateway for customer support tools"
  role_arn    = aws_iam_role.gateway.arn
  protocol_type = "MCP"
  authorizer_type = "CUSTOM_JWT"
  authorizer_configuration {
    custom_jwt_authorizer {
      discovery_url  = local.cognito_discovery_url
      allowed_scopes = [local.cognito_scope]
    }
  }
}

resource "aws_bedrockagentcore_gateway_target" "check_warranty_status" {
  name               = "check-warranty-status"
  gateway_identifier = aws_bedrockagentcore_gateway.customer_support.gateway_id
  description        = "Warranty coverage lookup by serial number"

  credential_provider_configuration {
    gateway_iam_role {}
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = aws_lambda_function.tool_check_warranty_status.arn

        tool_schema {
          inline_payload {
            name        = "check_warranty_status"
            description = "Check warranty coverage for a product given its serial number. Optionally verifies against the registered customer email."

            input_schema {
              type = "object"

              property {
                name        = "serial_number"
                type        = "string"
                description = "Product serial number to look up"
                required    = true
              }

              property {
                name        = "customer_email"
                type        = "string"
                description = "Customer email address to verify ownership (optional)"
                required    = false
              }
            }
          }
        }
      }
    }
  }
}

resource "local_file" "gateway_url" {
  content  = aws_bedrockagentcore_gateway.customer_support.gateway_url
  filename = "${path.root}/../tmp/gateway_url.txt"
}

resource "local_file" "gateway_id" {
  content  = aws_bedrockagentcore_gateway.customer_support.gateway_id
  filename = "${path.root}/../tmp/gateway_id.txt"
}

resource "local_file" "gateway_arn" {
  content  = aws_bedrockagentcore_gateway.customer_support.gateway_arn
  filename = "${path.root}/../tmp/gateway_arn.txt"
}

output "gateway_url" {
  value = aws_bedrockagentcore_gateway.customer_support.gateway_url
}

output "gateway_id" {
  value = aws_bedrockagentcore_gateway.customer_support.gateway_id
}
