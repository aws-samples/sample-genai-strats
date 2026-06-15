# ---- Gateway logs ----
resource "aws_cloudwatch_log_group" "gateway" {
  name              = "/aws/vendedlogs/bedrock-agentcore/gateway/${local.project_name}"
  retention_in_days = 7

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cloudwatch_log_delivery_source" "gateway_logs" {
  name         = "${local.project_name}-gateway-logs"
  log_type     = "APPLICATION_LOGS"
  resource_arn = awscc_bedrockagentcore_gateway.pizza_shop.gateway_arn
}

resource "aws_cloudwatch_log_delivery_destination" "gateway_logs" {
  name = "${local.project_name}-gateway-logs-dest"

  delivery_destination_type = "CWL"
  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.gateway.arn
  }

  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "gateway_logs" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.gateway_logs.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.gateway_logs.arn
}

# ---- Gateway traces ----
resource "aws_cloudwatch_log_delivery_source" "gateway_traces" {
  name         = "${local.project_name}-gateway-traces"
  log_type     = "TRACES"
  resource_arn = awscc_bedrockagentcore_gateway.pizza_shop.gateway_arn
}

resource "aws_cloudwatch_log_delivery_destination" "gateway_traces_xray" {
  name                      = "${local.project_name}-gateway-traces-xray"
  delivery_destination_type = "XRAY"
}

resource "aws_cloudwatch_log_delivery" "gateway_traces" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.gateway_traces.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.gateway_traces_xray.arn
}
