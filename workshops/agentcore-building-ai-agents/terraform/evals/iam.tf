# --- Role assumed by AgentCore Evaluations to read agent traces and write results
resource "aws_iam_role" "evals" {
  name = "${var.project_name}-agentcore-evals"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock-agentcore.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "evals" {
  role = aws_iam_role.evals.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Query agent traces in the agent's log groups only
        Effect = "Allow"
        Action = ["logs:StartQuery"]
        Resource = [
          "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/bedrock-agentcore/runtimes/${var.agent_runtime_id}-DEFAULT",
          "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/bedrock-agentcore/runtimes/${var.agent_runtime_id}-DEFAULT:*",
          "arn:aws:logs:${var.region}:${var.account_id}:log-group:aws/spans",
          "arn:aws:logs:${var.region}:${var.account_id}:log-group:aws/spans:*",
        ]
      },
      {
        # These actions don't support resource-level permissions
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:GetQueryResults",
          "logs:DescribeIndexPolicies",
        ]
        Resource = "*"
      },
      {
        # Write evaluation results
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/bedrock-agentcore/evaluations/*"
      },
    ]
  })
}
