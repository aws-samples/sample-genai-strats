# data "archive_file" "promotions_backend" {
#   type        = "zip"
#   output_path = "${path.root}/../tmp/promotions-backend.zip"

#   source {
#     filename = "index.mjs"
#     content  = <<-JS
#       export const handler = async (event) => {
#         const apiKey = (event.headers ?? {})["x-api-key"];
#         if (apiKey !== "workshop-demo-key") {
#           return {
#             statusCode: 401,
#             headers: { "Content-Type": "application/json" },
#             body: JSON.stringify({ message: "Unauthorized" }),
#           };
#         }
#         return {
#           statusCode: 200,
#           headers: { "Content-Type": "application/json" },
#           body: JSON.stringify({ promotions: "Buy two pizzas get one free!" }),
#         };
#       };
#     JS
#   }
# }

# resource "aws_iam_role" "promotions_backend" {
#   name = "${local.project_name}-promotions-backend"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect    = "Allow"
#       Principal = { Service = "lambda.amazonaws.com" }
#       Action    = "sts:AssumeRole"
#     }]
#   })
# }

# resource "aws_iam_role_policy_attachment" "promotions_backend_basic" {
#   role       = aws_iam_role.promotions_backend.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
# }

# resource "aws_lambda_function" "promotions_backend" {
#   function_name    = "${local.project_name}-promotions-backend"
#   filename         = data.archive_file.promotions_backend.output_path
#   source_code_hash = data.archive_file.promotions_backend.output_base64sha256
#   handler          = "index.handler"
#   runtime          = "nodejs22.x"
#   memory_size      = 256
#   role             = aws_iam_role.promotions_backend.arn
# }

# resource "aws_apigatewayv2_api" "promotions_backend" {
#   name          = "${local.project_name}-promotions-backend"
#   protocol_type = "HTTP"
# }

# resource "aws_apigatewayv2_integration" "promotions_backend" {
#   api_id                 = aws_apigatewayv2_api.promotions_backend.id
#   integration_type       = "AWS_PROXY"
#   integration_uri        = aws_lambda_function.promotions_backend.invoke_arn
#   payload_format_version = "2.0"
# }

# resource "aws_apigatewayv2_route" "promotions_backend" {
#   api_id    = aws_apigatewayv2_api.promotions_backend.id
#   route_key = "GET /promotions"
#   target    = "integrations/${aws_apigatewayv2_integration.promotions_backend.id}"
# }

# resource "aws_apigatewayv2_stage" "promotions_backend" {
#   api_id      = aws_apigatewayv2_api.promotions_backend.id
#   name        = "$default"
#   auto_deploy = true
# }

# resource "aws_lambda_permission" "promotions_backend" {
#   statement_id  = "AllowAPIGatewayInvoke"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.promotions_backend.function_name
#   principal     = "apigateway.amazonaws.com"
#   source_arn    = "${aws_apigatewayv2_api.promotions_backend.execution_arn}/*/*"
# }

# resource "local_file" "promotions_backend_url" {
#   content  = "${aws_apigatewayv2_stage.promotions_backend.invoke_url}/promotions"
#   filename = "${path.root}/../tmp/promotions_backend_url.txt"
# }

# resource "awscc_bedrockagentcore_policy" "allow_get_promotions" {
#   name             = "allow_get_promotions"
#   policy_engine_id = awscc_bedrockagentcore_policy_engine.pizza_shop.policy_engine_id
#   validation_mode  = "IGNORE_ALL_FINDINGS"

#   definition = {
#     cedar = {
#       statement = <<-EOT
#         permit(
#           principal,
#           action == AgentCore::Action::"promotions___get-promotions",
#           resource == AgentCore::Gateway::"${awscc_bedrockagentcore_gateway.pizza_shop.gateway_arn}"
#         );
#       EOT
#     }
#   }

#   depends_on = [aws_bedrockagentcore_gateway_target.promotions]
# }

# resource "aws_bedrockagentcore_api_key_credential_provider" "promotions" {
#   name              = "${local.project_name}-promotions"
#   api_key_wo        = "workshop-demo-key"
#   api_key_wo_version = 1
# }

# resource "aws_bedrockagentcore_gateway_target" "promotions" {
#   name               = "promotions"
#   gateway_identifier = awscc_bedrockagentcore_gateway.pizza_shop.gateway_identifier

#   credential_provider_configuration {
#     api_key {
#       provider_arn              = aws_bedrockagentcore_api_key_credential_provider.promotions.credential_provider_arn
#       credential_location       = "HEADER"
#       credential_parameter_name = "x-api-key"
#     }
#   }

#   target_configuration {
#     mcp {
#       open_api_schema {
#         inline_payload {
#           payload = jsonencode({
#             openapi = "3.0.0"
#             info = {
#               title   = "Promotions API"
#               version = "1.0.0"
#             }
#             servers = [{ url = aws_apigatewayv2_stage.promotions_backend.invoke_url }]
#             paths = {
#               "/promotions" = {
#                 get = {
#                   operationId = "get-promotions"
#                   summary     = "Returns current pizza promotions and special offers"
#                   responses = {
#                     "200" = {
#                       description = "Promotions"
#                       content = {
#                         "application/json" = {
#                           schema = {
#                             type = "object"
#                             properties = {
#                               promotions = { type = "string" }
#                             }
#                           }
#                         }
#                       }
#                     }
#                   }
#                 }
#               }
#             }
#           })
#         }
#       }
#     }
#   }
# }
