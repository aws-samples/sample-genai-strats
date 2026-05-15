# --- Authenticate Workday API Client ----
authenticate-api-client:
	cd workday-integration && \
		uv sync && \
		uv run authenticate_api_client.py

# --- Get A2A Agent Card via Workday API Client ----
get-a2a-agent-card:
	cd workday-integration && \
		uv sync && \
		uv run get_a2a_agent_card.py
	
	cp ./tmp/a2a_agent_card.json ./agent/a2a_agent_card.json

# --- Register MCP-Agent ---
register-mcp-agent:
	cd workday-integration && \
		uv sync && \
		uv run register_mcp_agent.py
		
# --- Build agent package
build-agent-package:
	rm -rf ./tmp/agent_package
	mkdir -p ./tmp
	cd agent && \
		uv pip install \
			--python-platform aarch64-manylinux2014 \
			--python-version 3.13 \
			--target=./../tmp/agent_package/dependencies \
			--only-binary=:all: \
			-r pyproject.toml
	cd tmp/agent_package/dependencies && zip -r ../agent.zip .
	cd agent && zip ./../tmp/agent_package/agent.zip *.py
	cd agent && zip ./../tmp/agent_package/agent.zip *.json

# --- Deploy AgentCore Resources ----
build-terraform-config:
	@test -n "$(MODE)" || (echo "ERROR: MODE is required"; exit 1)
	cd workday-integration && \
		uv sync && \
		MODE=$(MODE) uv run terraform_config_builder.py
	
	cp ./tmp/terraform.tfvars ./terraform/terraform.tfvars
	rm ./tmp/terraform.tfvars

deploy-infra:
	@echo "> Deploying infrastructure..."
	cd terraform && \
		terraform init && \
		terraform apply --auto-approve

deploy-a2a-agent-to-agentcore: 
	$(MAKE) build-agent-package
	$(MAKE) build-terraform-config MODE=A2A
	$(MAKE) deploy-infra

# deploy-mcp-agent-to-agentcore: 
# 	$(MAKE) build-agent-package
# 	$(MAKE) build-terraform-config MODE=MCP
# 	$(MAKE) deploy-infra

destroy:
	@echo "> Cleaning up..."
	cd terraform && terraform destroy
	rm -rf ./agent/a2a_agent_card.json
	rm -rf ./terraform/terraform.tfvars
	rm -rf ./tmp

# --- Workshop Tasks ----
run-chat-local:
	cd agent-chat && uv sync && uv run chat.py

run-chat-remote:
	cd agent-chat && uv sync && uv run chat.py remote

run-agent-locally:
	$(eval WORKLOAD_IDENTITY_NAME := $(shell cat ./tmp/workload_identity_name.txt))
	$(eval CREDENTIAL_PROVIDER_NAME := $(shell cat ./tmp/agent_client_credential_provider_name.txt))
	@test -n "$(MODE)" || (echo "ERROR: MODE is required, use MODE=A2A or MODE=MCP"; exit 1)

	@echo "WORKLOAD_IDENTITY_NAME=$(WORKLOAD_IDENTITY_NAME)"
	@echo "CREDENTIAL_PROVIDER_NAME=$(CREDENTIAL_PROVIDER_NAME)"
	@echo "MODE=$(MODE)"

	cd agent && \
		AGENT_MODE=$(MODE) \
		WORKLOAD_IDENTITY_NAME="$(WORKLOAD_IDENTITY_NAME)" \
		CREDENTIAL_PROVIDER_NAME="$(CREDENTIAL_PROVIDER_NAME)" \
		uv run agent.py

start-dashboard:
	@echo "> Start Dashboard..."
	$(eval AGENT_RUNTIME_ARN := $(shell cat ./tmp/agent_runtime_arn.txt))
	$(info > AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN))

	@rm -f ./dashboard/.env

	@echo "AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN)" >> ./dashboard-js/.env
	@echo "AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN)" >> ./dashboard-gradio/.env
	@echo "> .env updated"
	
	cd dashboard-js && npm install
	cd dashboard-js && node server.js

# 	cd dashboard-gradio && uv sync
# 	cd dashboard-gradio && uv run dashboard.py

