resource "aws_cognito_user_pool" "this" {
  name = local.project_name
}

resource "aws_cognito_user_pool_domain" "this" {
  domain       = local.project_name
  user_pool_id = aws_cognito_user_pool.this.id
}

resource "aws_cognito_resource_server" "gateway" {
  identifier   = "gateway"
  name         = "Gateway"
  user_pool_id = aws_cognito_user_pool.this.id

  scope {
    scope_name        = "invoke"
    scope_description = "Invoke the gateway"
  }

  # Pre-declaring fine-grained scopes to be used in Module 4
  scope {
    scope_name        = "get_menu"
    scope_description = "View the pizza menu"
  }
  scope {
    scope_name        = "create_order"
    scope_description = "Place a pizza order"
  }
}

resource "aws_cognito_user_pool_client" "mcp_client" {
  name         = "${local.project_name}-mcp-client"
  user_pool_id = aws_cognito_user_pool.this.id

  generate_secret                      = true
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_scopes                 = ["gateway/invoke"]
  supported_identity_providers         = ["COGNITO"]

  access_token_validity = 3
  token_validity_units {
    access_token = "hours"
  }

  depends_on = [ aws_cognito_resource_server.gateway ]
}

locals {
  cognito_issuer_url     = "https://cognito-idp.${data.aws_region.current.region}.amazonaws.com/${aws_cognito_user_pool.this.id}"
  cognito_discovery_url  = "${local.cognito_issuer_url}/.well-known/openid-configuration"
  cognito_token_endpoint = "https://${local.project_name}.auth.${data.aws_region.current.region}.amazoncognito.com/oauth2/token"
  cognito_scope          = "gateway/invoke"
}

resource "local_file" "cognito_token_endpoint" {
  content  = local.cognito_token_endpoint
  filename = "${path.root}/../tmp/cognito_token_endpoint.txt"
}

resource "local_file" "cognito_client_id" {
  content  = aws_cognito_user_pool_client.mcp_client.id
  filename = "${path.root}/../tmp/cognito_client_id.txt"
}

resource "local_file" "cognito_client_secret" {
  content  = aws_cognito_user_pool_client.mcp_client.client_secret
  filename = "${path.root}/../tmp/cognito_client_secret.txt"
}

resource "local_file" "cognito_scope" {
  content  = local.cognito_scope
  filename = "${path.root}/../tmp/cognito_scope.txt"
}
