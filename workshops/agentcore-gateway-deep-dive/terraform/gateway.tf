resource "awscc_bedrockagentcore_gateway" "pizza_shop" {
  name          = "${local.project_name}"
  description   = "MCP gateway for the pizza shop ordering tools"
  role_arn      = aws_iam_role.gateway.arn
  protocol_type = "MCP"
  
  authorizer_type = "NONE"

  # --- Module 3: comment out authorizer_type = "NONE" above and uncomment:
#   authorizer_type = "CUSTOM_JWT"
#   authorizer_configuration = {
#     custom_jwt_authorizer = {
#       discovery_url  = local.cognito_discovery_url
#       allowed_scopes = ["gateway/invoke"]
#     }
#   }

  # --- Module 4: Uncomment to attach the Policy Engine
#   policy_engine_configuration = {
#     arn  = awscc_bedrockagentcore_policy_engine.pizza_shop.policy_engine_arn
#     mode = "ENFORCE"
#   }

  # --- Module 5: Uncomment to attach the interceptor Lambda
#   interceptor_configurations = [
#     {
#       interception_points = ["REQUEST", "RESPONSE"]
#       interceptor = {
#         lambda = {
#           arn = aws_lambda_function.interceptor.arn
#         }
#       }
#       input_configuration = {
#         pass_request_headers = true
#       }
#     }
#   ]

  exception_level = "DEBUG"
}

resource "aws_bedrockagentcore_gateway_target" "get_menu" {
  name               = "get-menu"
  gateway_identifier = awscc_bedrockagentcore_gateway.pizza_shop.gateway_identifier

  credential_provider_configuration {
    gateway_iam_role {}
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = aws_lambda_function.get_menu.arn

        tool_schema {
          inline_payload {
            name        = "get-menu"
            description = "Returns the current pizza menu with item IDs, names, and prices"

            input_schema {
              type = "object"
            }
          }
        }
      }
    }
  }

  depends_on = [aws_lambda_function.get_menu]
}

resource "aws_bedrockagentcore_gateway_target" "create_order" {
  name               = "create-order"
  gateway_identifier = awscc_bedrockagentcore_gateway.pizza_shop.gateway_identifier

  credential_provider_configuration {
    gateway_iam_role {}
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = aws_lambda_function.create_order.arn

        tool_schema {
          inline_payload {
            name        = "create-order"
            description = "Place a pizza order. Always call get-menu first to confirm the pizzaId."

            input_schema {
              type = "object"

              property {
                name        = "pizzaId"
                type        = "integer"
                description = "The ID of the pizza to order (from get-menu)"
                required    = true
              }
            }
          }
        }
      }
    }
  }

  depends_on = [aws_lambda_function.create_order]
}

resource "local_file" "gateway_url" {
  content  = awscc_bedrockagentcore_gateway.pizza_shop.gateway_url
  filename = "${path.root}/../tmp/gateway_url.txt"
}

resource "local_file" "gateway_id" {
  content  = awscc_bedrockagentcore_gateway.pizza_shop.gateway_identifier
  filename = "${path.root}/../tmp/gateway_id.txt"
}

resource "local_file" "gateway_arn" {
  content  = awscc_bedrockagentcore_gateway.pizza_shop.gateway_arn
  filename = "${path.root}/../tmp/gateway_arn.txt"
}
