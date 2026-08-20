variable "client_id" {}
variable "client_secret" {}
variable "oauth2_authz_endpoint" {}
variable "oauth2_token_endpoint" {}
variable "oauth2_issuer" {}

resource "awscc_bedrockagentcore_o_auth_2_credential_provider" "workday" {
  name                       = local.project_name
  credential_provider_vendor = "CustomOauth2"

  oauth_2_provider_config_input = {
    custom_oauth_2_provider_config = {
      client_id     = var.client_id
      client_secret = var.client_secret

      client_authentication_method = "CLIENT_SECRET_POST"

      oauth_discovery = {
        authorization_server_metadata = {
          issuer                 = var.oauth2_issuer
          authorization_endpoint = var.oauth2_authz_endpoint
          token_endpoint         = var.oauth2_token_endpoint
          response_types         = ["code"]
        }
      }
    }
  }
}

resource "local_file" "credential_provider_name" {
  filename = "${path.module}/../tmp/credential_provider_name.txt"
  content  = awscc_bedrockagentcore_o_auth_2_credential_provider.workday.name
}

resource "local_file" "credential_provider_callback_url" {
  filename = "${path.module}/../tmp/credential_provider_callback_url.txt"
  content  = awscc_bedrockagentcore_o_auth_2_credential_provider.workday.callback_url
}


output "credential_provider_name" {
  value = awscc_bedrockagentcore_o_auth_2_credential_provider.workday.name
}

output "credential_provider_callback_url" {
  value = awscc_bedrockagentcore_o_auth_2_credential_provider.workday.callback_url
}
