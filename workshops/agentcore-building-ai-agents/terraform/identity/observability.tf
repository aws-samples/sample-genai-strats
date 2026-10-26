# --- WORKLOAD IDENTITY LOGS ----
resource "aws_cloudwatch_log_group" "identity_logs" {
  name              = "/aws/bedrock-agentcore/identity/${var.project_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_delivery_source" "identity_logs" {
  name         = "${var.project_name}-identity-logs"
  log_type     = "APPLICATION_LOGS"
  resource_arn = aws_bedrockagentcore_workload_identity.agent.workload_identity_arn
}

resource "aws_cloudwatch_log_delivery_destination" "identity_logs" {
  name = "${var.project_name}-identity-logs"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.identity_logs.arn
  }

  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "identity_logs" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.identity_logs.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.identity_logs.arn
}

# --- WORKLOAD IDENTITY TRACES ----
resource "aws_cloudwatch_log_delivery_source" "identity_traces" {
  name         = "${var.project_name}-identity-traces"
  log_type     = "TRACES"
  resource_arn = aws_bedrockagentcore_workload_identity.agent.workload_identity_arn
}

resource "aws_cloudwatch_log_delivery_destination" "identity_traces" {
  name                      = "${var.project_name}-identity-traces"
  delivery_destination_type = "XRAY"
}

resource "aws_cloudwatch_log_delivery" "identity_traces" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.identity_traces.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.identity_traces.arn
}

# --- CREDENTIAL PROVIDER TRACES ----
resource "aws_cloudwatch_log_delivery_source" "credential_provider_traces" {
  name         = "${var.project_name}-cred-provider-traces"
  log_type     = "TRACES"
  resource_arn = aws_bedrockagentcore_oauth2_credential_provider.cognito.credential_provider_arn
}

resource "aws_cloudwatch_log_delivery_destination" "credential_provider_traces" {
  name                      = "${var.project_name}-cred-provider-traces"
  delivery_destination_type = "XRAY"
}

resource "aws_cloudwatch_log_delivery" "credential_provider_traces" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.credential_provider_traces.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.credential_provider_traces.arn
}
