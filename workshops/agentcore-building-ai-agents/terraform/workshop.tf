# --- Module 2: Uncomment to deploy the Knowledge Base
# module "knowledge_base" {
#   source       = "./knowledge_base"
#   project_name = local.project_name
#   region       = data.aws_region.current.region
# }

# --- Module 3: Uncomment to deploy AgentCore Memory
# module "memory" {
#   source       = "./memory"
#   project_name = local.project_name
#   region       = data.aws_region.current.region
# }

# --- Module 4: Uncomment to deploy AgentCore Gateway
# module "gateway" {
#   source                        = "./gateway"
#   project_name                  = local.project_name
#   region                        = data.aws_region.current.region
# }

# --- Module 5: Uncomment to deploy AgentCore Identity
# module "identity" {
#   source                        = "./identity"
#   project_name                  = local.project_name
#   oauth2_provider_client_id     = module.gateway.cognito_client_id
#   oauth2_provider_client_secret = module.gateway.cognito_client_secret
#   oauth2_discovery_url          = module.gateway.cognito_discovery_url
# }

# --- Module 6: Uncomment to deploy AgentCore Runtime infrastructure
# module "runtime" {
#   source                        = "./runtime"
#   project_name                  = local.project_name
#   region                        = data.aws_region.current.region
#   agentcore_memory_id           = module.memory.memory_id
#   tech_support_knowledgebase_id = module.knowledge_base.kb_id
#   gateway_url                   = module.gateway.gateway_url
#   cognito_scope                 = module.gateway.cognito_scope
#   credential_provider_name      = module.identity.credential_provider_name
#   workload_identity_name        = module.identity.workload_identity_name
# }
