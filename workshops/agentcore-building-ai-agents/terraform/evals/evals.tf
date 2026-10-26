locals {
  project_name_underscore = replace(var.project_name, "-", "_")

  builtin_evaluators = [
    "Builtin.GoalSuccessRate",       # SESSION   - did the customer get what they came for
    "Builtin.Helpfulness",           # TRACE     - how useful the response is to the customer
    "Builtin.ToolSelectionAccuracy", # TOOL_CALL - picked the right tool for the request
    "Builtin.Faithfulness",          # TRACE     - response is supported by tool/KB results
    "Builtin.InstructionFollowing",  # TRACE     - follows the system prompt (e.g. plain text, no markdown)
    "Builtin.ToolParameterAccuracy", # TOOL_CALL - extracted tool parameters correctly
    "Builtin.Refusal",               # TRACE     - declined or evaded the request
    "Builtin.Harmfulness",           # TRACE     - safety baseline
    "Builtin.ResponseRelevance",     # TRACE     - addresses the question asked
    "Builtin.Correctness",           # TRACE     - factual accuracy
  ]

  # Runtime IDs are <runtime-name>-<suffix>. Agents on AgentCore Runtime report their OTEL
  # service name as <runtime-name>.<endpoint-name>
  agent_runtime_name = regex("^(.*)-[^-]+$", var.agent_runtime_id)[0]
  agent_service_name = "${local.agent_runtime_name}.DEFAULT"
  # Runtime log group with spans and OTEL event records (prompts, responses, tool calls)
  agent_log_group = "/aws/bedrock-agentcore/runtimes/${var.agent_runtime_id}-DEFAULT"
}

resource "aws_bedrockagentcore_online_evaluation_config" "agent" {
  online_evaluation_config_name = "${local.project_name_underscore}_online_evals"
  description                   = "Online evaluation of the customer support agent with built-in evaluators"
  evaluation_execution_role_arn = aws_iam_role.evals.arn
  enable_on_create              = true

  data_source_config {
    cloudwatch_logs {
      # aws/spans is where spans land when the agent sends them separately from event records
      log_group_names = [local.agent_log_group, "aws/spans"]
      service_names   = [local.agent_service_name]
    }
  }

  dynamic "evaluator" {
    for_each = local.builtin_evaluators
    content {
      evaluator_id = evaluator.value
    }
  }

  rule {
    # Evaluate every session - fine for a workshop, use a lower percentage in production
    sampling_config {
      sampling_percentage = 100
    }

    # A session is evaluated only after it has been idle for this long (default is 15 minutes).
    # 1 minute lets you see results shortly after the conversation ends. In production, set it
    # to the longest pause you expect within a real conversation, otherwise sessions get
    # evaluated before they are complete.
    session_config {
      session_timeout_minutes = 1
    }
  }

  depends_on = [aws_iam_role_policy.evals]
}
