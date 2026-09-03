resource "aws_cognito_user_pool" "this" {
  name = local.project_name
}

resource "aws_cognito_user_pool_domain" "this" {
  domain       = local.project_name
  user_pool_id = aws_cognito_user_pool.this.id
}

resource "aws_cognito_resource_server" "mcp_server" {
  identifier   = "mcp_server"
  name         = "mcp_server"
  user_pool_id = aws_cognito_user_pool.this.id

  scope {
    scope_name        = "access"
    scope_description = "access"
  }

}

resource "aws_cognito_user_pool_client" "this" {
  name                                 = "${local.project_name}-client"
  user_pool_id                         = aws_cognito_user_pool.this.id
  generate_secret                      = true
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_scopes                 = ["mcp_server/access"]
  supported_identity_providers         = ["COGNITO"]

  # Issue access tokens with the maximum lifetime Cognito allows (24 hours).
  access_token_validity = 24
  token_validity_units {
    access_token = "hours"
  }

  depends_on = [aws_cognito_resource_server.mcp_server]
}

locals {
  cognito_token_endpoint         = "https://${aws_cognito_user_pool_domain.this.domain}.auth.${data.aws_region.current.region}.amazoncognito.com/oauth2/token"
  cognito_authorization_endpoint = "https://${aws_cognito_user_pool_domain.this.domain}.auth.${data.aws_region.current.region}.amazoncognito.com/oauth2/authorize"
  cognito_issuer                 = "https://cognito-idp.${data.aws_region.current.region}.amazonaws.com/${aws_cognito_user_pool.this.id}"
  cognito_discovery_url          = "https://cognito-idp.${data.aws_region.current.region}.amazonaws.com/${aws_cognito_user_pool.this.id}/.well-known/openid-configuration"
}

resource "local_file" "cognito_client_id" {
  content  = aws_cognito_user_pool_client.this.id
  filename = "${path.root}/../tmp/cognito_client_id.txt"
}

resource "local_file" "cognito_client_secret" {
  content  = aws_cognito_user_pool_client.this.client_secret
  filename = "${path.root}/../tmp/cognito_client_secret.txt"
}


resource "local_file" "cognito_scopes" {
  content  = join(" ", aws_cognito_user_pool_client.this.allowed_oauth_scopes)
  filename = "${path.root}/../tmp/cognito_scopes.txt"
}

resource "local_file" "cognito_token_endpoint" {
  content  = local.cognito_token_endpoint
  filename = "${path.root}/../tmp/cognito_token_endpoint.txt"
}

resource "local_file" "cognito_discovery_url" {
  content  = local.cognito_discovery_url
  filename = "${path.root}/../tmp/cognito_discovery_url.txt"
}
