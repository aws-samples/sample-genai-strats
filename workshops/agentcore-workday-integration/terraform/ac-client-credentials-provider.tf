resource "aws_bedrockagentcore_oauth2_credential_provider" "workday_agent_client" {
  name                       = "${local.project_name}-workday-agent-client"
  credential_provider_vendor = "CustomOauth2"
  oauth2_provider_config {
    custom_oauth2_provider_config {
      client_id     = var.wd_agent_client_id
      client_secret = var.wd_agent_client_secret
      oauth_discovery {
        authorization_server_metadata {
          issuer = var.wd_agent_client_issuer
          authorization_endpoint = var.wd_agent_client_authz_endpoint
          token_endpoint = var.wd_agent_client_token_endpoint
          response_types = ["code"]
        }
      }
    }
  }
}

data "external" "agent_client_credential_provider_callback_url" {
  depends_on = [aws_bedrockagentcore_oauth2_credential_provider.workday_agent_client]

  program = ["bash", "-c",
    "aws bedrock-agentcore-control get-oauth2-credential-provider --name '${aws_bedrockagentcore_oauth2_credential_provider.workday_agent_client.name}' --query 'callbackUrl' --output text | jq -R '{callback_url: .}'"
  ]
}

output "agent_client_credential_provider_callback_url" {
  value = data.external.agent_client_credential_provider_callback_url.result["callback_url"]
}

# output "agent_client_credential_provider_name" {
#   value = aws_bedrockagentcore_oauth2_credential_provider.workday_agent_client.name
# }

resource "local_file" "agent_client_credential_provider_callback_url" {
    filename = "${path.root}/../tmp/agent_client_credential_provider_callback_url.txt"
    content = data.external.agent_client_credential_provider_callback_url.result["callback_url"]
}

resource "local_file" "agent_client_credential_provider_name" {
    filename = "${path.root}/../tmp/agent_client_credential_provider_name.txt"
    content = aws_bedrockagentcore_oauth2_credential_provider.workday_agent_client.name
}