# --- GATEWAY LOGS ----
resource "aws_cloudwatch_log_group" "gateway_logs" {
  name              = "/aws/bedrock-agentcore/gateway/${var.project_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_delivery_source" "gateway_logs" {
  name         = "${var.project_name}-gateway-logs"
  log_type     = "APPLICATION_LOGS"
  resource_arn = aws_bedrockagentcore_gateway.customer_support.gateway_arn
}

resource "aws_cloudwatch_log_delivery_destination" "gateway_logs" {
  name = "${var.project_name}-gateway-logs"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.gateway_logs.arn
  }

  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "gateway_logs" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.gateway_logs.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.gateway_logs.arn
}

# --- GATEWAY TRACES ----
resource "aws_cloudwatch_log_delivery_source" "gateway_traces" {
  name         = "${var.project_name}-gateway-traces"
  log_type     = "TRACES"
  resource_arn = aws_bedrockagentcore_gateway.customer_support.gateway_arn
}

resource "aws_cloudwatch_log_delivery_destination" "gateway_traces" {
  name = "${var.project_name}-gateway-traces"
  delivery_destination_type = "XRAY"
}

resource "aws_cloudwatch_log_delivery" "gateway_traces" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.gateway_traces.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.gateway_traces.arn
}