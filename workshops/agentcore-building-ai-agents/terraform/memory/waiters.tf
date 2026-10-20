# Memory goes into UPDATING state whenever a strategy is added or removed, and
# rejects further changes until it's back to ACTIVE. These waiters are chained
# between the memory and its strategies so that every create/delete step waits
# for ACTIVE. Destroy runs the chain in reverse.
#
# memory -> wait_0 -> preferences -> wait_1 -> semantic -> wait_2
#
# wait_2 gates the memory_id output and local_file, so downstream consumers
# only see the memory once all strategies exist and it's ACTIVE.

resource "terraform_data" "wait_0" {
  input = {
    memory_id = aws_bedrockagentcore_memory.customer_support.id
    region    = var.region
    script    = "${path.module}/wait-memory-active.sh"
  }

  provisioner "local-exec" {
    command = "bash ${self.input.script} ${self.input.memory_id} ${self.input.region}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "bash ${self.input.script} ${self.input.memory_id} ${self.input.region}"
  }
}

resource "terraform_data" "wait_1" {
  input = {
    memory_id = aws_bedrockagentcore_memory.customer_support.id
    region    = var.region
    script    = "${path.module}/wait-memory-active.sh"
  }

  provisioner "local-exec" {
    command = "bash ${self.input.script} ${self.input.memory_id} ${self.input.region}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "bash ${self.input.script} ${self.input.memory_id} ${self.input.region}"
  }

  depends_on = [aws_bedrockagentcore_memory_strategy.preferences]
}

resource "terraform_data" "wait_2" {
  input = {
    memory_id = aws_bedrockagentcore_memory.customer_support.id
    region    = var.region
    script    = "${path.module}/wait-memory-active.sh"
  }

  provisioner "local-exec" {
    command = "bash ${self.input.script} ${self.input.memory_id} ${self.input.region}"
  }

  depends_on = [aws_bedrockagentcore_memory_strategy.semantic]
}
