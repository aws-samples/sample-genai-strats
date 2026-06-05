variable "project_name" {}
variable "oauth2_provider_client_id" {}
variable "oauth2_provider_client_secret" {
    sensitive = true
    ephemeral = true
}
variable "oauth2_discovery_url" {}
