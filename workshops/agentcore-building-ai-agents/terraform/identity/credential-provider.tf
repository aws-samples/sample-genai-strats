resource "aws_bedrockagentcore_oauth2_credential_provider" "cognito" {
  name                       = "${var.project_name}-cognito"
  credential_provider_vendor = "CustomOauth2"
  oauth2_provider_config {
    custom_oauth2_provider_config {
        client_id_wo = var.oauth2_provider_client_id
        client_secret_wo = var.oauth2_provider_client_secret
        client_credentials_wo_version = 1
        oauth_discovery {
          discovery_url = var.oauth2_discovery_url
        }
    }
  }
}

output "credential_provider_name" {
  value = aws_bedrockagentcore_oauth2_credential_provider.cognito.name
}

resource "local_file" "credential_provider_name" {
    filename = "${path.root}/../tmp/credential_provider_name.txt"
    content = aws_bedrockagentcore_oauth2_credential_provider.cognito.name
}

