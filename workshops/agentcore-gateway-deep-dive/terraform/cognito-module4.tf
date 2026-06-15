# resource "aws_cognito_user_pool_client" "client1" {
#   name         = "${local.project_name}-client1"
#   user_pool_id = aws_cognito_user_pool.this.id

#   generate_secret                      = true
#   allowed_oauth_flows_user_pool_client = true
#   allowed_oauth_flows                  = ["client_credentials"]
#   allowed_oauth_scopes                 = ["gateway/get_menu"]
#   supported_identity_providers         = ["COGNITO"]
#
#   depends_on = [ aws_cognito_resource_server.gateway ]
# }

# resource "aws_cognito_user_pool_client" "client2" {
#   name         = "${local.project_name}-client2"
#   user_pool_id = aws_cognito_user_pool.this.id

#   generate_secret                      = true
#   allowed_oauth_flows_user_pool_client = true
#   allowed_oauth_flows                  = ["client_credentials"]
#   allowed_oauth_scopes                 = ["gateway/get_menu", "gateway/create_order"]
#   supported_identity_providers         = ["COGNITO"]
#
#   depends_on = [ aws_cognito_resource_server.gateway ]
# }

# resource "local_file" "cognito_client1_id" {
#   content  = aws_cognito_user_pool_client.client1.id
#   filename = "${path.root}/../tmp/cognito_client1_id.txt"
# }

# resource "local_file" "cognito_client1_secret" {
#   content  = aws_cognito_user_pool_client.client1.client_secret
#   filename = "${path.root}/../tmp/cognito_client1_secret.txt"
# }

# resource "local_file" "cognito_client2_id" {
#   content  = aws_cognito_user_pool_client.client2.id
#   filename = "${path.root}/../tmp/cognito_client2_id.txt"
# }

# resource "local_file" "cognito_client2_secret" {
#   content  = aws_cognito_user_pool_client.client2.client_secret
#   filename = "${path.root}/../tmp/cognito_client2_secret.txt"
# }
