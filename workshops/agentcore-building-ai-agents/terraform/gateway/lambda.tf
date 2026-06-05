resource "aws_iam_role" "gateway_lambda" {
  name = "${var.project_name}-gw-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "gateway_lambda_basic" {
  role       = aws_iam_role.gateway_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ── tool-check-warranty-status ───────────────────────────────────────────────
data "archive_file" "tool_check_warranty_status" {
  type        = "zip"
  source_dir  = "${path.root}/../src/lambdas/tool-check-warranty-status"
  output_path = "${path.root}/../tmp/tool-check-warranty-status.zip"
}

resource "aws_lambda_function" "tool_check_warranty_status" {
  function_name    = "${var.project_name}-tool-check-warranty-status"
  architectures    = ["arm64"]
  filename         = data.archive_file.tool_check_warranty_status.output_path
  source_code_hash = data.archive_file.tool_check_warranty_status.output_base64sha256
  role             = aws_iam_role.gateway_lambda.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.13"
  timeout          = 10
  memory_size      = 512

}

resource "aws_lambda_permission" "gateway_invoke_check_warranty_status" {
  statement_id  = "AllowBedrockAgentCoreGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tool_check_warranty_status.function_name
  principal     = "bedrock-agentcore.amazonaws.com"
  source_arn    = aws_bedrockagentcore_gateway.customer_support.gateway_arn
}
