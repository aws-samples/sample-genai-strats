resource "aws_bedrockagentcore_workload_identity" "hr_agent" {
  name = "${local.project_name}"
}

resource "local_file" "workload_identity_name" {
  filename = "${path.root}/../tmp/workload_identity_name.txt"
  content = aws_bedrockagentcore_workload_identity.hr_agent.name
}

# output "workload_identity_name" {
#   value = aws_bedrockagentcore_workload_identity.hr_agent.name
# }


resource "aws_cloudwatch_log_group" "wlid" {
  name              = "/aws/bedrock-agentcore/wlid"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_delivery_source" "wlid" {
  name         = "wlid"
  log_type     = "APPLICATION_LOGS"
  resource_arn = aws_bedrockagentcore_workload_identity.hr_agent.workload_identity_arn
}

resource "aws_cloudwatch_log_delivery_destination" "wlid" {
  name = "wlid"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.wlid.arn
  }

  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "wlid" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.wlid.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.wlid.arn
}
