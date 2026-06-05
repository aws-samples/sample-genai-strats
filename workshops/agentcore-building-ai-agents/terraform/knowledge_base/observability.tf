resource "aws_cloudwatch_log_group" "kb_logs" {
  name              = "/aws/bedrock/knowledge-base/${var.project_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_delivery_source" "kb" {
  name         = "${var.project_name}-kb"
  log_type     = "APPLICATION_LOGS"
  resource_arn = aws_bedrockagent_knowledge_base.tech_support.arn
}

resource "aws_cloudwatch_log_delivery_destination" "kb" {
  name = "${var.project_name}-kb"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.kb_logs.arn
  }

  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "kb" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.kb.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.kb.arn
}
