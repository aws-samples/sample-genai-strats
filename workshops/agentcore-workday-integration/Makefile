# --- Register mcp-agent ---
register-external-agent:
	cd workday-integration && \
		uv sync && \
		uv run register_external_agent.py

get-mcp-agent-access-token:
	cd workday-integration && \
		uv sync && \
		uv run get_mcp_agent_access_token.py

get-a2a-agent-access-token:
	cd workday-integration && \
		uv sync && \
		uv run get_a2a_agent_access_token.py

build-agent-package:
# 	rm -rf ./tmp/agent_package
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

deploy-mcp-agent-to-agentcore: 
	$(MAKE) build-agent-package
	$(MAKE) build-terraform-config MODE=mcp
	$(MAKE) deploy-infra

deploy-a2a-agent-to-agentcore: 
	$(MAKE) build-agent-package
	$(MAKE) build-terraform-config MODE=a2a
	$(MAKE) deploy-infra

destroy:
	@echo "> Cleaning up..."
	cd terraform && terraform destroy
	rm -rf ./terraform/terraform.tfvars
	rm -rf ./tmp

run-agent-locally:
	$(eval WORKLOAD_IDENTITY_NAME := $(shell cat ./tmp/workload_identity_name.txt))
	$(eval CREDENTIAL_PROVIDER_NAME := $(shell cat ./tmp/credential_provider_name.txt))
	$(eval ACCESS_TOKEN := $(shell cat ./tmp/$(if $(filter a2a,$(MODE)),a2a,mcp)_agent_access_token.txt))
	$(eval MCP_ENDPOINT := https://api.eu.wcp.workday.com/robotgw/coremcp)
	$(eval A2A_AGENT_CARD_BASE_URL := https://eu.agent.workday.com/v1/a2a/devcon_wcpdev169/self-service-agent)

	@test -n "$(MODE)" || (echo "ERROR: MODE is required, use MODE=a2a or MODE=mcp"; exit 1)

	@echo "WORKLOAD_IDENTITY_NAME=$(WORKLOAD_IDENTITY_NAME)"
	@echo "CREDENTIAL_PROVIDER_NAME=$(CREDENTIAL_PROVIDER_NAME)"
	@echo "ACCESS_TOKEN=$(shell echo '$(ACCESS_TOKEN)' | cut -c1-10)...REDACTED..."
	@echo "MCP_ENDPOINT=$(MCP_ENDPOINT)"
	@echo "A2A_AGENT_CARD_BASE_URL=$(A2A_AGENT_CARD_BASE_URL)"
	@echo "MODE=$(MODE)"

	@cd agent && \
		AGENT_MODE=$(MODE) \
		WORKLOAD_IDENTITY_NAME="$(WORKLOAD_IDENTITY_NAME)" \
		CREDENTIAL_PROVIDER_NAME="$(CREDENTIAL_PROVIDER_NAME)" \
		MCP_ENDPOINT="$(MCP_ENDPOINT)" \
		A2A_AGENT_CARD_BASE_URL="$(A2A_AGENT_CARD_BASE_URL)" \
		ACCESS_TOKEN="$(ACCESS_TOKEN)" \
		uv run agent.py

start-dashboard:
	@echo "> Start Dashboard..."
	$(eval AGENT_RUNTIME_ARN := $(shell cat ./tmp/agent_runtime_arn.txt))
	$(info > AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN))

	@rm -f ./dashboard/.env
	@echo "AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN)" >> ./dashboard-js/.env
	
	cd dashboard-js && npm install
	cd dashboard-js && node server.js

run-orchestration-lab:
		cd orchestration && \
		uv sync && \
		uv run chat.py
