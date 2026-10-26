locals {
  project_name_underscored = replace(var.project_name, "-", "_")
}

resource "aws_bedrockagentcore_memory" "customer_support" {
  name                  = "${local.project_name_underscored}_customer_support"
  description           = "Customer support agent memory"
  event_expiry_duration = 7
}

resource "aws_bedrockagentcore_memory_strategy" "preferences" {
  name                = "CustomerSupportPreferences"
  description         = "Captures customer preferences and behavior"
  memory_id           = aws_bedrockagentcore_memory.customer_support.id
  type                = "USER_PREFERENCE"
  namespace_templates = ["support/customer/{actorId}/preferences/"]
  depends_on          = [terraform_data.wait_0]
}

resource "aws_bedrockagentcore_memory_strategy" "semantic" {
  name                = "CustomerSupportSemantic"
  description         = "Stores facts from customer support conversations"
  memory_id           = aws_bedrockagentcore_memory.customer_support.id
  type                = "SEMANTIC"
  namespace_templates = ["support/customer/{actorId}/semantic/"]
  depends_on          = [terraform_data.wait_1]
}

resource "local_file" "memory_id" {
  content  = aws_bedrockagentcore_memory.customer_support.id
  filename = "${path.root}/../tmp/memory_id.txt"

  depends_on = [terraform_data.wait_2]
}

output "memory_id" {
  value = aws_bedrockagentcore_memory.customer_support.id

  depends_on = [terraform_data.wait_2]
}
