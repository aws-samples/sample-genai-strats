resource "awscc_bedrockagentcore_policy_engine" "pizza_shop" {
  name = local.project_name_underscore
}

# Module 4 - Step 6: Permit all (illustration only - overly permissive)
# resource "awscc_bedrockagentcore_policy" "permit_all" {
#   name             = "permit_all"
#   policy_engine_id = awscc_bedrockagentcore_policy_engine.pizza_shop.policy_engine_id
#   validation_mode  = "IGNORE_ALL_FINDINGS"

#   definition = {
#     cedar = {
#       statement = "permit(principal, action, resource is AgentCore::Gateway);"
#     }
#   }

#   depends_on = [
#     aws_bedrockagentcore_gateway_target.get_menu,
#     aws_bedrockagentcore_gateway_target.create_order,
#   ]
# }

# Module 4 - Step 7: Permit only get-menu for all principals
# resource "awscc_bedrockagentcore_policy" "allow_get_menu" {
#   name             = "allow_get_menu"
#   policy_engine_id = awscc_bedrockagentcore_policy_engine.pizza_shop.policy_engine_id
#   validation_mode  = "IGNORE_ALL_FINDINGS"

#   definition = {
#     cedar = {
#       statement = <<-EOT
#         permit(
#           principal,
#           action == AgentCore::Action::"get-menu___get-menu",
#           resource == AgentCore::Gateway::"${awscc_bedrockagentcore_gateway.pizza_shop.gateway_arn}"
#         );
#       EOT
#     }
#   }

#   depends_on = [ aws_bedrockagentcore_gateway_target.get_menu ]
# }

# Module 4 - Step 8: Permit create-order only if token has gateway/create_order scope
# resource "awscc_bedrockagentcore_policy" "allow_create_order_with_scope" {
#   name             = "allow_create_order_with_scope"
#   policy_engine_id = awscc_bedrockagentcore_policy_engine.pizza_shop.policy_engine_id
#   validation_mode  = "IGNORE_ALL_FINDINGS"

#   definition = {
#     cedar = {
#       statement = <<-EOT
#         permit(
#           principal,
#           action == AgentCore::Action::"create-order___create-order",
#           resource == AgentCore::Gateway::"${awscc_bedrockagentcore_gateway.pizza_shop.gateway_arn}"
#         )
#         when {
#           principal.hasTag("scope") &&
#           principal.getTag("scope") like "*gateway/create_order*"
#         };
#       EOT
#     }
#   }

#  depends_on = [ aws_bedrockagentcore_gateway_target.create_order ]
# }

# Module 4 - Step 9: Forbid ordering Pineapple Deluxe (id=5) for everyone
# resource "awscc_bedrockagentcore_policy" "forbid_pineapple" {
#   name             = "forbid_pineapple"
#   policy_engine_id = awscc_bedrockagentcore_policy_engine.pizza_shop.policy_engine_id
#   validation_mode  = "IGNORE_ALL_FINDINGS"

#   definition = {
#     cedar = {
#       statement = <<-EOT
#         forbid(
#           principal,
#           action == AgentCore::Action::"create-order___create-order",
#           resource == AgentCore::Gateway::"${awscc_bedrockagentcore_gateway.pizza_shop.gateway_arn}"
#         )
#         when {
#           context.input.pizzaId == 5
#         };
#       EOT
#     }
#   }

#  depends_on = [ aws_bedrockagentcore_gateway_target.create_order ]
# }
