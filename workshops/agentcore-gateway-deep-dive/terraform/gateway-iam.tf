resource "aws_iam_role" "gateway" {
  name = "${local.project_name}-agentcore-gw"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock-agentcore.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "gateway" {
  name = "gateway"
  role = aws_iam_role.gateway.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = [
          aws_lambda_function.get_menu.arn,
          aws_lambda_function.create_order.arn,
          aws_lambda_function.interceptor.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:*",
          "xray:*",
          "bedrock-agentcore:*"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "secretsmanager:GetSecretValue"
        Resource = "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:bedrock-agentcore-identity!default/apikey/*"
      }
    ]
  })
}