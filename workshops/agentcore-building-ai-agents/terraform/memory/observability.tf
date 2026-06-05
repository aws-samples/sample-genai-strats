# --- MEMORY LOGS ----
resource "aws_cloudwatch_log_group" "memory_logs" {
  name              = "/aws/bedrock-agentcore/memory/${var.project_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_delivery_source" "memory_logs" {
  name         = "${var.project_name}-memory-logs"
  log_type     = "APPLICATION_LOGS"
  resource_arn = aws_bedrockagentcore_memory.customer_support.arn
}

resource "aws_cloudwatch_log_delivery_destination" "memory_logs" {
  name = "${var.project_name}-memory-logs"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.memory_logs.arn
  }

  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "memory_logs" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.memory_logs.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.memory_logs.arn
}

# --- MEMORY TRACES ----
resource "aws_cloudwatch_log_delivery_source" "memory_traces" {
  name         = "${var.project_name}-memory-traces"
  log_type     = "TRACES"
  resource_arn = aws_bedrockagentcore_memory.customer_support.arn
}

resource "aws_cloudwatch_log_delivery_destination" "memory_traces" {
  name = "${var.project_name}-memory-traces"
  delivery_destination_type = "XRAY"
}

resource "aws_cloudwatch_log_delivery" "memory_traces" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.memory_traces.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.memory_traces.arn
}