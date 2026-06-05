# --- RUNTIME APPLICATION LOGS ----
resource "aws_cloudwatch_log_group" "runtime_logs" {
  name              = "/aws/bedrock-agentcore/runtime/applogs/${var.project_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_delivery_source" "runtime_logs" {
  name         = "${var.project_name}-runtime-logs"
  log_type     = "APPLICATION_LOGS"
  resource_arn = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
}

resource "aws_cloudwatch_log_delivery_destination" "runtime_logs" {
  name = "${var.project_name}-runtime-logs"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.runtime_logs.arn
  }

  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "runtime_logs" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.runtime_logs.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.runtime_logs.arn
}

# --- RUNTIME TRACES ----
resource "aws_cloudwatch_log_delivery_source" "runtime_traces" {
  name         = "${var.project_name}-runtime-traces"
  log_type     = "TRACES"
  resource_arn = aws_bedrockagentcore_agent_runtime.agent.agent_runtime_arn
}

resource "aws_cloudwatch_log_delivery_destination" "runtime_traces" {
  name = "${var.project_name}-runtime-traces"
  delivery_destination_type = "XRAY"
}

resource "aws_cloudwatch_log_delivery" "runtime_traces" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.runtime_traces.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.runtime_traces.arn
}
